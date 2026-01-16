"""
Combo Normalizer

Provides normalization functions for consistent combo comparison:
- Band sorting (LTE first ascending, then NR ascending)
- BCS normalization
- Component deduplication
"""

from typing import Dict, List, Set, Optional
from ..models import (
    ComboType,
    BandComponent,
    Combo,
    ComboSet,
)


class Normalizer:
    """Normalize combos for consistent comparison."""

    @staticmethod
    def normalize_combo(combo: Combo) -> Combo:
        """
        Normalize a single combo for consistent comparison.

        Normalization rules:
        1. Sort components: LTE bands first (ascending), then NR bands (ascending)
        2. Normalize band class to uppercase
        3. Deduplicate identical components

        Args:
            combo: Combo to normalize

        Returns:
            New normalized Combo object
        """
        # Normalize each component
        normalized_components = []
        seen = set()

        for comp in combo.components:
            # Normalize band class
            norm_comp = BandComponent(
                band=comp.band,
                band_class=comp.band_class.upper(),
                mimo_layers=comp.mimo_layers,
                is_nr=comp.is_nr,
            )

            # Deduplicate
            comp_key = (norm_comp.band, norm_comp.band_class, norm_comp.is_nr)
            if comp_key not in seen:
                seen.add(comp_key)
                normalized_components.append(norm_comp)

        # Sort: LTE first (is_nr=False), then NR (is_nr=True), then by band number
        sorted_components = sorted(
            normalized_components,
            key=lambda c: (c.is_nr, c.band, c.band_class)
        )

        return Combo(
            combo_type=combo.combo_type,
            components=sorted_components,
            bcs=combo.bcs,
            fallback_list=combo.fallback_list,
            source=combo.source,
            raw_string=combo.raw_string,
        )

    @staticmethod
    def normalize_combo_set(combo_set: ComboSet) -> ComboSet:
        """
        Normalize all combos in a ComboSet.

        Args:
            combo_set: ComboSet to normalize

        Returns:
            New normalized ComboSet
        """
        normalized = ComboSet(
            source=combo_set.source,
            combo_type=combo_set.combo_type,
        )

        for combo in combo_set.values():
            norm_combo = Normalizer.normalize_combo(combo)
            normalized.add(norm_combo)

        return normalized

    @staticmethod
    def normalize_band_class(band_class: str) -> str:
        """
        Normalize bandwidth class to standard format.

        Args:
            band_class: Raw band class string

        Returns:
            Normalized uppercase band class
        """
        return band_class.upper().strip()

    @staticmethod
    def normalize_bcs(bcs: Optional[Set[int]]) -> Optional[Set[int]]:
        """
        Normalize BCS (Bandwidth Combination Set).

        Args:
            bcs: Set of BCS values or None

        Returns:
            Normalized BCS set or None
        """
        if bcs is None:
            return None

        # Remove invalid BCS values (valid: 0-31 for LTE, 0-15 for NR typically)
        # We'll be lenient and accept 0-255
        valid_bcs = {b for b in bcs if 0 <= b <= 255}
        return valid_bcs if valid_bcs else None

    @staticmethod
    def get_canonical_key(combo: Combo) -> str:
        """
        Generate a canonical key for a combo.

        This key is used for comparison between different sources.
        Format: "LTE1A-LTE2B-n77A-n78C" (sorted, deduplicated)

        Args:
            combo: Combo to generate key for

        Returns:
            Canonical string key
        """
        norm_combo = Normalizer.normalize_combo(combo)
        return norm_combo.normalized_key

    @staticmethod
    def combos_equivalent(combo1: Combo, combo2: Combo) -> bool:
        """
        Check if two combos are equivalent (same bands/classes, ignoring MIMO).

        Args:
            combo1: First combo
            combo2: Second combo

        Returns:
            True if combos are equivalent
        """
        key1 = Normalizer.get_canonical_key(combo1)
        key2 = Normalizer.get_canonical_key(combo2)
        return key1 == key2

    @staticmethod
    def bcs_matches(bcs1: Optional[Set[int]], bcs2: Optional[Set[int]]) -> bool:
        """
        Check if two BCS sets match.

        Matching rules:
        - Both None: match
        - One None, one set: match (lenient - None means "all")
        - Both sets: must have at least one common value

        Args:
            bcs1: First BCS set
            bcs2: Second BCS set

        Returns:
            True if BCS sets match
        """
        if bcs1 is None or bcs2 is None:
            return True

        # Both have values - check for intersection
        return len(bcs1 & bcs2) > 0

    @staticmethod
    def group_by_band_count(combo_set: ComboSet) -> Dict[int, List[Combo]]:
        """
        Group combos by number of bands.

        Args:
            combo_set: ComboSet to group

        Returns:
            Dict mapping band count to list of combos
        """
        groups: Dict[int, List[Combo]] = {}

        for combo in combo_set.values():
            count = len(combo.components)
            if count not in groups:
                groups[count] = []
            groups[count].append(combo)

        return groups

    @staticmethod
    def group_by_combo_type(combo_set: ComboSet) -> Dict[ComboType, List[Combo]]:
        """
        Group combos by type (LTE_CA, ENDC, etc.).

        Args:
            combo_set: ComboSet to group

        Returns:
            Dict mapping ComboType to list of combos
        """
        groups: Dict[ComboType, List[Combo]] = {}

        for combo in combo_set.values():
            ctype = combo.combo_type
            if ctype not in groups:
                groups[ctype] = []
            groups[ctype].append(combo)

        return groups

    @staticmethod
    def extract_unique_bands(combo_set: ComboSet) -> Dict[str, Set[int]]:
        """
        Extract unique bands from a ComboSet.

        Args:
            combo_set: ComboSet to analyze

        Returns:
            Dict with 'lte' and 'nr' keys mapping to sets of band numbers
        """
        lte_bands: Set[int] = set()
        nr_bands: Set[int] = set()

        for combo in combo_set.values():
            for comp in combo.components:
                if comp.is_nr:
                    nr_bands.add(comp.band)
                else:
                    lte_bands.add(comp.band)

        return {
            'lte': lte_bands,
            'nr': nr_bands,
        }
