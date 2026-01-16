"""
Unit tests for Combos Module Data Models
"""

import pytest
from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    BandComponent,
    Combo,
    ComboSet,
    Discrepancy,
    ComparisonResult,
)


class TestBandComponent:
    """Tests for BandComponent dataclass."""

    def test_lte_band_str(self):
        """Test LTE band string representation."""
        comp = BandComponent(band=66, band_class='A', is_nr=False)
        assert str(comp) == '66A'

    def test_nr_band_str(self):
        """Test NR band string representation."""
        comp = BandComponent(band=77, band_class='A', is_nr=True)
        assert str(comp) == 'n77A'

    def test_band_hash(self):
        """Test band component hashing."""
        comp1 = BandComponent(band=66, band_class='A', is_nr=False)
        comp2 = BandComponent(band=66, band_class='A', is_nr=False)
        assert hash(comp1) == hash(comp2)

    def test_band_equality(self):
        """Test band component equality."""
        comp1 = BandComponent(band=66, band_class='A', is_nr=False)
        comp2 = BandComponent(band=66, band_class='A', is_nr=False)
        comp3 = BandComponent(band=66, band_class='B', is_nr=False)
        assert comp1 == comp2
        assert comp1 != comp3

    def test_band_mimo(self):
        """Test band with MIMO layers."""
        comp = BandComponent(band=66, band_class='A', mimo_layers=4, is_nr=False)
        assert comp.mimo_layers == 4
        assert str(comp) == '66A'  # MIMO not in string repr


class TestCombo:
    """Tests for Combo dataclass."""

    def test_lte_ca_combo(self):
        """Test LTE CA combo creation."""
        components = [
            BandComponent(band=1, band_class='A', is_nr=False),
            BandComponent(band=3, band_class='A', is_nr=False),
        ]
        combo = Combo(combo_type=ComboType.LTE_CA, components=components)

        assert combo.combo_type == ComboType.LTE_CA
        assert len(combo.components) == 2
        assert len(combo.lte_components) == 2
        assert len(combo.nr_components) == 0

    def test_endc_combo(self):
        """Test EN-DC combo creation."""
        components = [
            BandComponent(band=66, band_class='A', is_nr=False),
            BandComponent(band=77, band_class='A', is_nr=True),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        assert combo.combo_type == ComboType.ENDC
        assert len(combo.lte_components) == 1
        assert len(combo.nr_components) == 1

    def test_normalized_key_sorting(self):
        """Test normalized key sorts LTE before NR."""
        components = [
            BandComponent(band=77, band_class='A', is_nr=True),
            BandComponent(band=66, band_class='A', is_nr=False),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        # LTE (66A) should come before NR (n77A)
        assert combo.normalized_key == '66A-n77A'

    def test_normalized_key_lte_sorting(self):
        """Test normalized key sorts LTE bands by number."""
        components = [
            BandComponent(band=7, band_class='A', is_nr=False),
            BandComponent(band=3, band_class='A', is_nr=False),
            BandComponent(band=1, band_class='A', is_nr=False),
        ]
        combo = Combo(combo_type=ComboType.LTE_CA, components=components)

        assert combo.normalized_key == '1A-3A-7A'

    def test_combo_equality(self):
        """Test combo equality based on normalized key."""
        components1 = [
            BandComponent(band=77, band_class='A', is_nr=True),
            BandComponent(band=66, band_class='A', is_nr=False),
        ]
        components2 = [
            BandComponent(band=66, band_class='A', is_nr=False),
            BandComponent(band=77, band_class='A', is_nr=True),
        ]
        combo1 = Combo(combo_type=ComboType.ENDC, components=components1)
        combo2 = Combo(combo_type=ComboType.ENDC, components=components2)

        assert combo1 == combo2
        assert hash(combo1) == hash(combo2)

    def test_combo_bands_property(self):
        """Test bands property returns all band numbers."""
        components = [
            BandComponent(band=66, band_class='A', is_nr=False),
            BandComponent(band=77, band_class='A', is_nr=True),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        assert combo.bands == {66, 77}


class TestComboSet:
    """Tests for ComboSet dataclass."""

    def test_add_combo(self):
        """Test adding combo to set."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)

        components = [
            BandComponent(band=1, band_class='A', is_nr=False),
            BandComponent(band=3, band_class='A', is_nr=False),
        ]
        combo = Combo(combo_type=ComboType.LTE_CA, components=components)

        combo_set.add(combo)

        assert len(combo_set) == 1
        assert combo.normalized_key in combo_set

    def test_no_duplicates(self):
        """Test duplicate combos are not added twice."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)

        components = [
            BandComponent(band=1, band_class='A', is_nr=False),
            BandComponent(band=3, band_class='A', is_nr=False),
        ]

        combo1 = Combo(combo_type=ComboType.LTE_CA, components=components.copy())
        combo2 = Combo(combo_type=ComboType.LTE_CA, components=components.copy())

        combo_set.add(combo1)
        combo_set.add(combo2)

        assert len(combo_set) == 1

    def test_get_combo(self):
        """Test getting combo by key."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)

        components = [
            BandComponent(band=1, band_class='A', is_nr=False),
        ]
        combo = Combo(combo_type=ComboType.LTE_CA, components=components)
        combo_set.add(combo)

        retrieved = combo_set.get('1A')
        assert retrieved is not None
        assert retrieved.normalized_key == '1A'

    def test_iteration(self):
        """Test iterating over combo set."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)

        for band in [1, 3, 7]:
            components = [BandComponent(band=band, band_class='A', is_nr=False)]
            combo_set.add(Combo(combo_type=ComboType.LTE_CA, components=components))

        keys = [c.normalized_key for c in combo_set]
        assert len(keys) == 3
        assert '1A' in keys
        assert '3A' in keys
        assert '7A' in keys


class TestComparisonResult:
    """Tests for ComparisonResult dataclass."""

    def test_match_percentage_all_common(self):
        """Test 100% match when all combos are common."""
        result = ComparisonResult(
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
            combo_type=ComboType.LTE_CA,
            common={'1A', '3A', '7A'},
            only_in_a=set(),
            only_in_b=set(),
        )

        assert result.match_percentage == 100.0
        assert result.total_discrepancies == 0

    def test_match_percentage_with_differences(self):
        """Test match percentage with differences."""
        result = ComparisonResult(
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
            combo_type=ComboType.LTE_CA,
            common={'1A', '3A'},  # 2 common
            only_in_a={'7A'},  # 1 missing
            only_in_b={'66A'},  # 1 extra
        )

        # 2 common out of 4 total = 50%
        assert result.match_percentage == 50.0
        assert result.total_discrepancies == 2

    def test_empty_comparison(self):
        """Test empty comparison returns 100%."""
        result = ComparisonResult(
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
            combo_type=ComboType.LTE_CA,
        )

        assert result.match_percentage == 100.0
        assert result.total_discrepancies == 0


class TestDiscrepancy:
    """Tests for Discrepancy dataclass."""

    def test_discrepancy_severity_from_reason(self):
        """Test severity comes from reason when provided."""
        from ..models import ReasoningResult

        components = [BandComponent(band=1, band_class='A', is_nr=False)]
        combo = Combo(combo_type=ComboType.LTE_CA, components=components)

        reason = ReasoningResult(
            has_explanation=True,
            reason_type='regional',
            explanation='Band not available in region',
            severity='expected'
        )

        disc = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
            reason=reason,
        )

        assert disc.severity == 'expected'

    def test_discrepancy_default_severity(self):
        """Test default severity when no reason provided."""
        components = [BandComponent(band=1, band_class='A', is_nr=False)]
        combo = Combo(combo_type=ComboType.LTE_CA, components=components)

        disc = Discrepancy(
            discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
            combo=combo,
            source_a=DataSource.RFC,
            source_b=DataSource.RRC_TABLE,
        )

        assert disc.severity == 'medium'
