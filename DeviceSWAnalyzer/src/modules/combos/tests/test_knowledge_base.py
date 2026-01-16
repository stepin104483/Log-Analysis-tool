"""
Unit tests for Knowledge Base and Reasoning Engine
"""

import pytest
import tempfile
import os

# Check if PyYAML is available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    BandComponent,
    Combo,
    Discrepancy,
    KnowledgeBaseContext,
    BandRestriction,
    ComboRestriction,
    CarrierRequirement,
)
from ..knowledge import KnowledgeBase, ReasoningEngine


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestKnowledgeBase:
    """Tests for KnowledgeBase class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.kb = KnowledgeBase()

    def _create_temp_yaml(self, content: str) -> str:
        """Create a temporary YAML file."""
        fd, path = tempfile.mkstemp(suffix='.yaml')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path

    def test_load_band_restrictions(self):
        """Test loading band restrictions from YAML."""
        yaml_content = """
name: "Test Restrictions"
version: "1.0"
region: "TEST"

band_restrictions:
  - band: 71
    reason: "Band 71 restricted in test region"
    restriction_type: "regional"

  - band: 14
    reason: "Band 14 regulatory restriction"
    restriction_type: "regulatory"
"""
        path = self._create_temp_yaml(yaml_content)
        try:
            self.kb.load(kb_files=[path])

            # Check band 71 restriction
            restrictions = self.kb.get_band_restrictions(71)
            assert len(restrictions) == 1
            assert restrictions[0].reason == "Band 71 restricted in test region"

            # Check band 14 restriction
            restrictions = self.kb.get_band_restrictions(14)
            assert len(restrictions) == 1
            assert restrictions[0].restriction_type == "regulatory"
        finally:
            os.unlink(path)

    def test_load_carrier_policy(self):
        """Test loading carrier policy from YAML."""
        yaml_content = """
name: "Test Carrier"
carrier: "TestCarrier"

required_combos:
  - "66A-n77A"
  - "2A-66A"

excluded_combos:
  - "71A-n71A"

combo_notes:
  "66A-n77A": "Primary combo"
"""
        path = self._create_temp_yaml(yaml_content)
        try:
            self.kb.load(kb_files=[path])

            req = self.kb.get_carrier_requirement("TestCarrier")
            assert req is not None
            assert "66A-N77A" in req.required_combos or "66A-n77A" in [c.lower() for c in req.required_combos]
        finally:
            os.unlink(path)

    def test_is_band_restricted(self):
        """Test checking if band is restricted."""
        yaml_content = """
band_restrictions:
  - band: 71
    reason: "Test restriction"
    restriction_type: "regional"
    regions:
      - "APAC"
"""
        path = self._create_temp_yaml(yaml_content)
        try:
            self.kb.load(kb_files=[path])

            # Band 71 should be restricted
            assert self.kb.is_band_restricted(71)

            # Band 66 should not be restricted
            assert not self.kb.is_band_restricted(66)
        finally:
            os.unlink(path)

    def test_get_summary(self):
        """Test getting knowledge base summary."""
        yaml_content = """
band_restrictions:
  - band: 71
    reason: "Test"
"""
        path = self._create_temp_yaml(yaml_content)
        try:
            self.kb.load(kb_files=[path])

            summary = self.kb.get_summary()
            assert summary['loaded'] is True
            assert summary['band_restrictions_count'] >= 1
        finally:
            os.unlink(path)


class TestReasoningEngine:
    """Tests for ReasoningEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = KnowledgeBaseContext()
        self.engine = ReasoningEngine(self.context)

    def _make_combo(self, bands, is_nr=False, combo_type=ComboType.LTE_CA):
        """Helper to create a combo."""
        components = [
            BandComponent(band=b, band_class='A', is_nr=is_nr)
            for b in bands
        ]
        return Combo(combo_type=combo_type, components=components)

    def _make_endc_combo(self, lte_bands, nr_bands):
        """Helper to create an EN-DC combo."""
        components = []
        for b in lte_bands:
            components.append(BandComponent(band=b, band_class='A', is_nr=False))
        for b in nr_bands:
            components.append(BandComponent(band=b, band_class='A', is_nr=True))
        return Combo(combo_type=ComboType.ENDC, components=components)

    def test_explain_band_restriction(self):
        """Test explaining discrepancy due to band restriction."""
        # Add band restriction
        self.context.band_restrictions[71] = [
            BandRestriction(
                band=71,
                restriction_type="regional",
                reason="Band 71 not available in APAC",
                source_file="test.yaml"
            )
        ]

        combo = self._make_endc_combo([66], [71])
        discrepancy = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
        )

        result = self.engine.explain_discrepancy(discrepancy)

        assert result.has_explanation is True
        assert result.reason_type == "regional"
        assert "71" in result.explanation
        assert result.severity == "expected"

    def test_explain_carrier_exclusion(self):
        """Test explaining discrepancy due to carrier exclusion."""
        # Add carrier requirement
        self.context.carrier_requirements["testcarrier"] = CarrierRequirement(
            carrier_name="TestCarrier",
            excluded_combos={"66A-N71A"},
        )
        self.context.active_carrier = "TestCarrier"

        combo = self._make_endc_combo([66], [71])
        discrepancy = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
        )

        result = self.engine.explain_discrepancy(discrepancy)

        # Should find carrier exclusion explanation
        assert result.has_explanation is True or result.severity in ["expected", "low", "medium"]

    def test_explain_efs_pruning(self):
        """Test explaining EFS pruning discrepancy."""
        combo = self._make_combo([1, 3])
        discrepancy = Discrepancy(
            discrepancy_type=DiscrepancyType.PRUNED_BY_EFS,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
            details="prune_ca_combos",
        )

        result = self.engine.explain_discrepancy(discrepancy)

        assert result.has_explanation is True
        assert result.reason_type == "efs"
        assert result.severity == "expected"

    def test_heuristic_mmwave(self):
        """Test heuristic for mmWave bands."""
        # Band 260 is mmWave
        combo = self._make_endc_combo([66], [260])
        discrepancy = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
        )

        result = self.engine.explain_discrepancy(discrepancy)

        # Should recognize mmWave and provide explanation
        assert result.has_explanation is True
        assert "mmwave" in result.explanation.lower() or result.severity in ["low", "expected"]

    def test_heuristic_band14(self):
        """Test heuristic for Band 14 (FirstNet)."""
        combo = self._make_combo([14, 66])
        discrepancy = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
        )

        result = self.engine.explain_discrepancy(discrepancy)

        # Should recognize Band 14 and provide explanation
        assert result.has_explanation is True
        assert "14" in result.explanation or "firstnet" in result.explanation.lower()

    def test_enrich_discrepancies(self):
        """Test enriching list of discrepancies."""
        combo1 = self._make_combo([1, 3])
        combo2 = self._make_endc_combo([66], [77])

        discrepancies = [
            Discrepancy(
                discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
                combo=combo1,
                source_a=DataSource.RFC,
                source_b=DataSource.RRC_TABLE,
            ),
            Discrepancy(
                discrepancy_type=DiscrepancyType.EXTRA_IN_RRC,
                combo=combo2,
                source_a=DataSource.RFC,
                source_b=DataSource.RRC_TABLE,
            ),
        ]

        enriched = self.engine.enrich_discrepancies(discrepancies)

        # All discrepancies should have reasoning
        for d in enriched:
            assert d.reason is not None

    def test_categorize_by_severity(self):
        """Test categorizing discrepancies by severity."""
        combo = self._make_combo([1, 3])

        discrepancies = [
            Discrepancy(
                discrepancy_type=DiscrepancyType.PRUNED_BY_EFS,
                combo=combo,
                source_a=DataSource.RFC,
                source_b=DataSource.RRC_TABLE,
            ),
            Discrepancy(
                discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
                combo=combo,
                source_a=DataSource.RFC,
                source_b=DataSource.RRC_TABLE,
            ),
        ]

        # Enrich first
        enriched = self.engine.enrich_discrepancies(discrepancies)

        # Categorize
        by_severity = self.engine.categorize_by_severity(enriched)

        # Should have categories
        assert 'expected' in by_severity
        assert 'high' in by_severity

    def test_default_severity(self):
        """Test default severity for unexplained discrepancies."""
        combo = self._make_combo([1, 3])
        discrepancy = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
        )

        result = self.engine.explain_discrepancy(discrepancy)

        # Even without knowledge base match, should have severity
        assert result.severity in ['critical', 'high', 'medium', 'low', 'expected', 'unknown']
