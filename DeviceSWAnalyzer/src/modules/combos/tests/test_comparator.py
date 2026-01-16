"""
Unit tests for Comparator
"""

import pytest
from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    BandComponent,
    Combo,
    ComboSet,
)
from ..analyzers.comparator import Comparator


class TestComparator:
    """Tests for Comparator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.comparator = Comparator()

    def _make_combo(self, bands, is_nr=False, combo_type=ComboType.LTE_CA):
        """Helper to create a combo from band list."""
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

    def test_compare_identical_sets(self):
        """Test comparing identical combo sets."""
        set_a = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        set_b = ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)

        for bands in [[1, 3], [1, 7], [3, 7]]:
            set_a.add(self._make_combo(bands))
            set_b.add(self._make_combo(bands))

        result = self.comparator.compare(set_a, set_b)

        assert len(result.common) == 3
        assert len(result.only_in_a) == 0
        assert len(result.only_in_b) == 0
        assert result.match_percentage == 100.0

    def test_compare_with_missing_in_b(self):
        """Test comparing when combos are missing from B."""
        set_a = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        set_b = ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)

        set_a.add(self._make_combo([1, 3]))
        set_a.add(self._make_combo([1, 7]))  # Missing in B
        set_b.add(self._make_combo([1, 3]))

        result = self.comparator.compare(set_a, set_b)

        assert len(result.common) == 1
        assert len(result.only_in_a) == 1
        assert '1A-7A' in result.only_in_a
        assert result.match_percentage == 50.0

    def test_compare_with_extra_in_b(self):
        """Test comparing when B has extra combos."""
        set_a = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        set_b = ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)

        set_a.add(self._make_combo([1, 3]))
        set_b.add(self._make_combo([1, 3]))
        set_b.add(self._make_combo([66]))  # Extra in B

        result = self.comparator.compare(set_a, set_b)

        assert len(result.common) == 1
        assert len(result.only_in_b) == 1
        assert '66A' in result.only_in_b

    def test_compare_empty_sets(self):
        """Test comparing empty combo sets."""
        set_a = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        set_b = ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)

        result = self.comparator.compare(set_a, set_b)

        assert len(result.common) == 0
        assert len(result.only_in_a) == 0
        assert len(result.only_in_b) == 0
        assert result.match_percentage == 100.0

    def test_compare_rfc_vs_rrc(self):
        """Test RFC vs RRC comparison generates discrepancies."""
        rfc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        }
        rrc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)
        }

        # RFC has 3 combos
        rfc_combos[ComboType.LTE_CA].add(self._make_combo([1, 3]))
        rfc_combos[ComboType.LTE_CA].add(self._make_combo([1, 7]))
        rfc_combos[ComboType.LTE_CA].add(self._make_combo([3, 7]))

        # RRC only has 2 (missing 3,7)
        rrc_combos[ComboType.LTE_CA].add(self._make_combo([1, 3]))
        rrc_combos[ComboType.LTE_CA].add(self._make_combo([1, 7]))

        results, discrepancies = self.comparator.compare_rfc_vs_rrc(rfc_combos, rrc_combos)

        # Should have 1 discrepancy (missing in RRC)
        missing = [d for d in discrepancies if d.discrepancy_type == DiscrepancyType.MISSING_IN_RRC]
        assert len(missing) == 1
        assert str(missing[0].combo) == '3A-7A'

    def test_compare_rfc_vs_rrc_extra(self):
        """Test RFC vs RRC detects extra combos in RRC."""
        rfc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        }
        rrc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)
        }

        rfc_combos[ComboType.LTE_CA].add(self._make_combo([1, 3]))
        rrc_combos[ComboType.LTE_CA].add(self._make_combo([1, 3]))
        rrc_combos[ComboType.LTE_CA].add(self._make_combo([66]))  # Extra

        results, discrepancies = self.comparator.compare_rfc_vs_rrc(rfc_combos, rrc_combos)

        extra = [d for d in discrepancies if d.discrepancy_type == DiscrepancyType.EXTRA_IN_RRC]
        assert len(extra) == 1
        assert str(extra[0].combo) == '66A'

    def test_compare_rrc_vs_uecap(self):
        """Test RRC vs UE Cap comparison."""
        rrc_combos = {
            ComboType.ENDC: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.ENDC)
        }
        uecap_combos = {
            ComboType.ENDC: ComboSet(source=DataSource.UE_CAP, combo_type=ComboType.ENDC)
        }

        # RRC has 2 combos
        rrc_combos[ComboType.ENDC].add(self._make_endc_combo([66], [77]))
        rrc_combos[ComboType.ENDC].add(self._make_endc_combo([2], [77]))

        # UE Cap only has 1
        uecap_combos[ComboType.ENDC].add(self._make_endc_combo([66], [77]))

        results, discrepancies = self.comparator.compare_rrc_vs_uecap(rrc_combos, uecap_combos)

        missing = [d for d in discrepancies if d.discrepancy_type == DiscrepancyType.MISSING_IN_UECAP]
        assert len(missing) == 1
        assert '2A' in str(missing[0].combo)

    def test_compare_multiple_combo_types(self):
        """Test comparison handles multiple combo types."""
        rfc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA),
            ComboType.ENDC: ComboSet(source=DataSource.RFC, combo_type=ComboType.ENDC),
        }
        rrc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA),
            ComboType.ENDC: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.ENDC),
        }

        # LTE CA
        rfc_combos[ComboType.LTE_CA].add(self._make_combo([1, 3]))
        rrc_combos[ComboType.LTE_CA].add(self._make_combo([1, 3]))

        # EN-DC (missing in RRC)
        rfc_combos[ComboType.ENDC].add(self._make_endc_combo([66], [77]))

        results, discrepancies = self.comparator.compare_rfc_vs_rrc(rfc_combos, rrc_combos)

        assert ComboType.LTE_CA in results
        assert ComboType.ENDC in results

        # LTE_CA should have 100% match
        assert results[ComboType.LTE_CA].match_percentage == 100.0

        # EN-DC should have 1 missing
        missing_endc = [d for d in discrepancies
                       if d.discrepancy_type == DiscrepancyType.MISSING_IN_RRC
                       and d.combo.combo_type == ComboType.ENDC]
        assert len(missing_endc) == 1

    def test_generate_summary_stats(self):
        """Test summary statistics generation."""
        rfc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA),
        }
        rrc_combos = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA),
        }

        # Add combos
        for bands in [[1], [3], [7]]:
            rfc_combos[ComboType.LTE_CA].add(self._make_combo(bands))
            rrc_combos[ComboType.LTE_CA].add(self._make_combo(bands))

        rfc_vs_rrc, _ = self.comparator.compare_rfc_vs_rrc(rfc_combos, rrc_combos)

        summary = self.comparator.generate_summary_stats(
            rfc_combos=rfc_combos,
            rrc_combos=rrc_combos,
            uecap_combos=None,
            rfc_vs_rrc=rfc_vs_rrc,
            rrc_vs_uecap=None,
        )

        assert summary['total_combos']['rfc'] == 3
        assert summary['total_combos']['rrc'] == 3
        assert summary['comparisons']['rfc_vs_rrc']['match_percentage'] == 100.0
        assert 1 in summary['unique_bands']['lte']
        assert 3 in summary['unique_bands']['lte']
        assert 7 in summary['unique_bands']['lte']

    def test_bcs_mismatch_detection(self):
        """Test BCS mismatch is detected."""
        set_a = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)
        set_b = ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA)

        # Same combo but different BCS
        combo_a = self._make_combo([1, 3])
        combo_a.bcs = {0, 1}
        set_a.add(combo_a)

        combo_b = self._make_combo([1, 3])
        combo_b.bcs = {2, 3}  # Different BCS with no overlap
        set_b.add(combo_b)

        result = self.comparator.compare(set_a, set_b)

        assert len(result.bcs_mismatches) == 1
        assert result.bcs_mismatches[0].discrepancy_type == DiscrepancyType.BCS_MISMATCH
