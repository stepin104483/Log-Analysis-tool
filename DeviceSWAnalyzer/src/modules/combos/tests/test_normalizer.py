"""
Unit tests for Normalizer
"""

import pytest
from ..models import (
    ComboType,
    DataSource,
    BandComponent,
    Combo,
    ComboSet,
)
from ..analyzers.normalizer import Normalizer


class TestNormalizer:
    """Tests for Normalizer class."""

    def test_normalize_combo_band_class_uppercase(self):
        """Test band class is normalized to uppercase."""
        components = [
            BandComponent(band=66, band_class='a', is_nr=False),
            BandComponent(band=77, band_class='b', is_nr=True),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        normalized = Normalizer.normalize_combo(combo)

        assert normalized.components[0].band_class == 'A'
        assert normalized.components[1].band_class == 'B'

    def test_normalize_combo_sorting(self):
        """Test components are sorted: LTE first, then NR, by band number."""
        components = [
            BandComponent(band=77, band_class='A', is_nr=True),
            BandComponent(band=7, band_class='A', is_nr=False),
            BandComponent(band=3, band_class='A', is_nr=False),
            BandComponent(band=78, band_class='A', is_nr=True),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        normalized = Normalizer.normalize_combo(combo)

        # Should be: 3A, 7A (LTE sorted), n77A, n78A (NR sorted)
        assert normalized.components[0].band == 3
        assert normalized.components[0].is_nr is False
        assert normalized.components[1].band == 7
        assert normalized.components[1].is_nr is False
        assert normalized.components[2].band == 77
        assert normalized.components[2].is_nr is True
        assert normalized.components[3].band == 78
        assert normalized.components[3].is_nr is True

    def test_normalize_combo_deduplication(self):
        """Test duplicate components are removed."""
        components = [
            BandComponent(band=66, band_class='A', is_nr=False),
            BandComponent(band=66, band_class='A', is_nr=False),  # Duplicate
            BandComponent(band=77, band_class='A', is_nr=True),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        normalized = Normalizer.normalize_combo(combo)

        assert len(normalized.components) == 2

    def test_normalize_combo_preserves_metadata(self):
        """Test BCS and other metadata are preserved."""
        components = [BandComponent(band=66, band_class='A', is_nr=False)]
        combo = Combo(
            combo_type=ComboType.LTE_CA,
            components=components,
            bcs={0, 1, 2},
            source=DataSource.RFC,
            raw_string='B66A',
        )

        normalized = Normalizer.normalize_combo(combo)

        assert normalized.bcs == {0, 1, 2}
        assert normalized.source == DataSource.RFC
        assert normalized.raw_string == 'B66A'

    def test_normalize_combo_set(self):
        """Test normalizing entire combo set."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)

        components = [
            BandComponent(band=7, band_class='a', is_nr=False),
            BandComponent(band=3, band_class='a', is_nr=False),
        ]
        combo_set.add(Combo(combo_type=ComboType.LTE_CA, components=components))

        normalized_set = Normalizer.normalize_combo_set(combo_set)

        assert len(normalized_set) == 1
        combo = list(normalized_set.values())[0]
        assert combo.normalized_key == '3A-7A'

    def test_get_canonical_key(self):
        """Test canonical key generation."""
        components = [
            BandComponent(band=77, band_class='a', is_nr=True),
            BandComponent(band=66, band_class='b', is_nr=False),
        ]
        combo = Combo(combo_type=ComboType.ENDC, components=components)

        key = Normalizer.get_canonical_key(combo)

        assert key == '66B-n77A'

    def test_combos_equivalent(self):
        """Test combo equivalence check."""
        components1 = [
            BandComponent(band=66, band_class='A', is_nr=False),
            BandComponent(band=77, band_class='A', is_nr=True),
        ]
        components2 = [
            BandComponent(band=77, band_class='a', is_nr=True),  # Different order & case
            BandComponent(band=66, band_class='a', is_nr=False),
        ]
        combo1 = Combo(combo_type=ComboType.ENDC, components=components1)
        combo2 = Combo(combo_type=ComboType.ENDC, components=components2)

        assert Normalizer.combos_equivalent(combo1, combo2)

    def test_bcs_matches_both_none(self):
        """Test BCS match when both are None."""
        assert Normalizer.bcs_matches(None, None) is True

    def test_bcs_matches_one_none(self):
        """Test BCS match when one is None (lenient)."""
        assert Normalizer.bcs_matches(None, {0, 1}) is True
        assert Normalizer.bcs_matches({0, 1}, None) is True

    def test_bcs_matches_with_intersection(self):
        """Test BCS match when sets have intersection."""
        assert Normalizer.bcs_matches({0, 1, 2}, {1, 2, 3}) is True

    def test_bcs_matches_no_intersection(self):
        """Test BCS mismatch when no intersection."""
        assert Normalizer.bcs_matches({0, 1}, {2, 3}) is False

    def test_group_by_band_count(self):
        """Test grouping combos by band count."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA)

        # Add 2-band combo
        combo_set.add(Combo(
            combo_type=ComboType.LTE_CA,
            components=[
                BandComponent(band=1, band_class='A', is_nr=False),
                BandComponent(band=3, band_class='A', is_nr=False),
            ]
        ))

        # Add 3-band combo
        combo_set.add(Combo(
            combo_type=ComboType.LTE_CA,
            components=[
                BandComponent(band=1, band_class='A', is_nr=False),
                BandComponent(band=3, band_class='A', is_nr=False),
                BandComponent(band=7, band_class='A', is_nr=False),
            ]
        ))

        groups = Normalizer.group_by_band_count(combo_set)

        assert 2 in groups
        assert 3 in groups
        assert len(groups[2]) == 1
        assert len(groups[3]) == 1

    def test_extract_unique_bands(self):
        """Test extracting unique LTE and NR bands."""
        combo_set = ComboSet(source=DataSource.RFC, combo_type=ComboType.ENDC)

        combo_set.add(Combo(
            combo_type=ComboType.ENDC,
            components=[
                BandComponent(band=66, band_class='A', is_nr=False),
                BandComponent(band=77, band_class='A', is_nr=True),
            ]
        ))
        combo_set.add(Combo(
            combo_type=ComboType.ENDC,
            components=[
                BandComponent(band=2, band_class='A', is_nr=False),
                BandComponent(band=77, band_class='A', is_nr=True),
            ]
        ))

        bands = Normalizer.extract_unique_bands(combo_set)

        assert bands['lte'] == {66, 2}
        assert bands['nr'] == {77}

    def test_normalize_bcs_valid(self):
        """Test BCS normalization with valid values."""
        bcs = {0, 1, 2, 15, 31}
        normalized = Normalizer.normalize_bcs(bcs)

        assert normalized == {0, 1, 2, 15, 31}

    def test_normalize_bcs_none(self):
        """Test BCS normalization with None."""
        assert Normalizer.normalize_bcs(None) is None

    def test_normalize_bcs_filters_invalid(self):
        """Test BCS normalization filters invalid values."""
        bcs = {-1, 0, 1, 256, 300}  # -1 and 300 are invalid
        normalized = Normalizer.normalize_bcs(bcs)

        assert normalized == {0, 1}  # Only valid values (0-255)
