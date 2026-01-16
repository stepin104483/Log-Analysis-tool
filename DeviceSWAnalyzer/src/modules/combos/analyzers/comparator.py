"""
Combo Comparator

Compares ComboSets from different sources to find discrepancies:
- Missing combos (in A but not B)
- Extra combos (in B but not A)
- BCS mismatches
"""

from typing import Dict, List, Set, Tuple, Optional
from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    Combo,
    ComboSet,
    Discrepancy,
    ComparisonResult,
)
from .normalizer import Normalizer


class Comparator:
    """Compare ComboSets from different sources."""

    def __init__(self):
        self.normalizer = Normalizer()

    def compare(
        self,
        source_a: ComboSet,
        source_b: ComboSet,
    ) -> ComparisonResult:
        """
        Compare two ComboSets and return comparison result.

        Args:
            source_a: First ComboSet (typically RFC or expected)
            source_b: Second ComboSet (typically RRC/built or actual)

        Returns:
            ComparisonResult with common, only_in_a, only_in_b, and mismatches
        """
        # Get normalized keys from both sources
        keys_a = source_a.keys()
        keys_b = source_b.keys()

        # Set operations
        common = keys_a & keys_b
        only_in_a = keys_a - keys_b
        only_in_b = keys_b - keys_a

        # Check for BCS mismatches in common combos
        bcs_mismatches = []
        for key in common:
            combo_a = source_a.get(key)
            combo_b = source_b.get(key)

            if combo_a and combo_b:
                if not Normalizer.bcs_matches(combo_a.bcs, combo_b.bcs):
                    discrepancy = Discrepancy(
                        discrepancy_type=DiscrepancyType.BCS_MISMATCH,
                        combo=combo_a,
                        source_a=source_a.source,
                        source_b=source_b.source,
                        details=f"BCS mismatch: {combo_a.bcs} vs {combo_b.bcs}",
                    )
                    bcs_mismatches.append(discrepancy)

        return ComparisonResult(
            source_a=source_a.source,
            source_b=source_b.source,
            combo_type=source_a.combo_type,
            common=common,
            only_in_a=only_in_a,
            only_in_b=only_in_b,
            bcs_mismatches=bcs_mismatches,
        )

    def compare_rfc_vs_rrc(
        self,
        rfc_combos: Dict[ComboType, ComboSet],
        rrc_combos: Dict[ComboType, ComboSet],
    ) -> Tuple[Dict[ComboType, ComparisonResult], List[Discrepancy]]:
        """
        Compare RFC combos against RRC table combos.

        Identifies:
        - MISSING_IN_RRC: Combos in RFC but not built in RRC table
        - EXTRA_IN_RRC: Combos in RRC table but not defined in RFC

        Args:
            rfc_combos: Dict of ComboSets from RFC
            rrc_combos: Dict of ComboSets from RRC table

        Returns:
            Tuple of (comparison results by type, all discrepancies)
        """
        results = {}
        all_discrepancies = []

        for combo_type in ComboType:
            rfc_set = rfc_combos.get(combo_type)
            rrc_set = rrc_combos.get(combo_type)

            if rfc_set is None:
                rfc_set = ComboSet(source=DataSource.RFC, combo_type=combo_type)
            if rrc_set is None:
                rrc_set = ComboSet(source=DataSource.RRC_TABLE, combo_type=combo_type)

            comparison = self.compare(rfc_set, rrc_set)
            results[combo_type] = comparison

            # Create discrepancy objects for missing/extra combos
            for key in comparison.only_in_a:
                combo = rfc_set.get(key)
                if combo:
                    discrepancy = Discrepancy(
                        discrepancy_type=DiscrepancyType.MISSING_IN_RRC,
                        combo=combo,
                        source_a=DataSource.RFC,
                        source_b=DataSource.RRC_TABLE,
                        details=f"Combo defined in RFC but not found in RRC table",
                    )
                    all_discrepancies.append(discrepancy)

            for key in comparison.only_in_b:
                combo = rrc_set.get(key)
                if combo:
                    discrepancy = Discrepancy(
                        discrepancy_type=DiscrepancyType.EXTRA_IN_RRC,
                        combo=combo,
                        source_a=DataSource.RFC,
                        source_b=DataSource.RRC_TABLE,
                        details=f"Combo in RRC table but not defined in RFC",
                    )
                    all_discrepancies.append(discrepancy)

            # Add BCS mismatches
            all_discrepancies.extend(comparison.bcs_mismatches)

        return results, all_discrepancies

    def compare_rrc_vs_uecap(
        self,
        rrc_combos: Dict[ComboType, ComboSet],
        uecap_combos: Dict[ComboType, ComboSet],
    ) -> Tuple[Dict[ComboType, ComparisonResult], List[Discrepancy]]:
        """
        Compare RRC table combos against UE Capability advertisement.

        Identifies:
        - MISSING_IN_UECAP: Combos in RRC table but not advertised
        - Extra combos in UE Cap (shouldn't happen normally)

        Args:
            rrc_combos: Dict of ComboSets from RRC table
            uecap_combos: Dict of ComboSets from UE Capability

        Returns:
            Tuple of (comparison results by type, all discrepancies)
        """
        results = {}
        all_discrepancies = []

        for combo_type in ComboType:
            rrc_set = rrc_combos.get(combo_type)
            uecap_set = uecap_combos.get(combo_type)

            if rrc_set is None:
                rrc_set = ComboSet(source=DataSource.RRC_TABLE, combo_type=combo_type)
            if uecap_set is None:
                uecap_set = ComboSet(source=DataSource.UE_CAP, combo_type=combo_type)

            comparison = self.compare(rrc_set, uecap_set)
            results[combo_type] = comparison

            # Combos in RRC but not in UE Cap
            for key in comparison.only_in_a:
                combo = rrc_set.get(key)
                if combo:
                    discrepancy = Discrepancy(
                        discrepancy_type=DiscrepancyType.MISSING_IN_UECAP,
                        combo=combo,
                        source_a=DataSource.RRC_TABLE,
                        source_b=DataSource.UE_CAP,
                        details=f"Combo in RRC table but not advertised in UE Capability",
                    )
                    all_discrepancies.append(discrepancy)

            # Add BCS mismatches
            all_discrepancies.extend(comparison.bcs_mismatches)

        return results, all_discrepancies

    def generate_summary_stats(
        self,
        rfc_combos: Optional[Dict[ComboType, ComboSet]],
        rrc_combos: Optional[Dict[ComboType, ComboSet]],
        uecap_combos: Optional[Dict[ComboType, ComboSet]],
        rfc_vs_rrc: Optional[Dict[ComboType, ComparisonResult]],
        rrc_vs_uecap: Optional[Dict[ComboType, ComparisonResult]],
    ) -> Dict:
        """
        Generate summary statistics for all comparisons.

        Args:
            rfc_combos: RFC combo sets
            rrc_combos: RRC combo sets
            uecap_combos: UE Cap combo sets
            rfc_vs_rrc: RFC vs RRC comparison results
            rrc_vs_uecap: RRC vs UE Cap comparison results

        Returns:
            Dict with summary statistics
        """
        summary = {
            'total_combos': {
                'rfc': 0,
                'rrc': 0,
                'uecap': 0,
            },
            'by_type': {},
            'comparisons': {
                'rfc_vs_rrc': {
                    'total_discrepancies': 0,
                    'missing_in_rrc': 0,
                    'extra_in_rrc': 0,
                    'bcs_mismatches': 0,
                    'match_percentage': 0.0,
                },
                'rrc_vs_uecap': {
                    'total_discrepancies': 0,
                    'missing_in_uecap': 0,
                    'bcs_mismatches': 0,
                    'match_percentage': 0.0,
                },
            },
            'unique_bands': {
                'lte': set(),
                'nr': set(),
            },
        }

        # Count totals by source and type
        for combo_type in ComboType:
            type_stats = {
                'rfc': 0,
                'rrc': 0,
                'uecap': 0,
            }

            if rfc_combos and combo_type in rfc_combos:
                count = len(rfc_combos[combo_type])
                type_stats['rfc'] = count
                summary['total_combos']['rfc'] += count

            if rrc_combos and combo_type in rrc_combos:
                count = len(rrc_combos[combo_type])
                type_stats['rrc'] = count
                summary['total_combos']['rrc'] += count

            if uecap_combos and combo_type in uecap_combos:
                count = len(uecap_combos[combo_type])
                type_stats['uecap'] = count
                summary['total_combos']['uecap'] += count

            summary['by_type'][combo_type.name] = type_stats

        # RFC vs RRC comparison stats
        if rfc_vs_rrc:
            total_missing = 0
            total_extra = 0
            total_bcs = 0
            total_match_pct = []

            for combo_type, result in rfc_vs_rrc.items():
                total_missing += len(result.only_in_a)
                total_extra += len(result.only_in_b)
                total_bcs += len(result.bcs_mismatches)
                if len(result.common) + len(result.only_in_a) + len(result.only_in_b) > 0:
                    total_match_pct.append(result.match_percentage)

            summary['comparisons']['rfc_vs_rrc'] = {
                'total_discrepancies': total_missing + total_extra + total_bcs,
                'missing_in_rrc': total_missing,
                'extra_in_rrc': total_extra,
                'bcs_mismatches': total_bcs,
                'match_percentage': sum(total_match_pct) / len(total_match_pct) if total_match_pct else 100.0,
            }

        # RRC vs UE Cap comparison stats
        if rrc_vs_uecap:
            total_missing = 0
            total_bcs = 0
            total_match_pct = []

            for combo_type, result in rrc_vs_uecap.items():
                total_missing += len(result.only_in_a)
                total_bcs += len(result.bcs_mismatches)
                if len(result.common) + len(result.only_in_a) + len(result.only_in_b) > 0:
                    total_match_pct.append(result.match_percentage)

            summary['comparisons']['rrc_vs_uecap'] = {
                'total_discrepancies': total_missing + total_bcs,
                'missing_in_uecap': total_missing,
                'bcs_mismatches': total_bcs,
                'match_percentage': sum(total_match_pct) / len(total_match_pct) if total_match_pct else 100.0,
            }

        # Extract unique bands
        for source_combos in [rfc_combos, rrc_combos, uecap_combos]:
            if source_combos:
                for combo_set in source_combos.values():
                    bands = Normalizer.extract_unique_bands(combo_set)
                    summary['unique_bands']['lte'].update(bands['lte'])
                    summary['unique_bands']['nr'].update(bands['nr'])

        # Convert sets to sorted lists for JSON serialization
        summary['unique_bands']['lte'] = sorted(summary['unique_bands']['lte'])
        summary['unique_bands']['nr'] = sorted(summary['unique_bands']['nr'])

        return summary


def compare_combo_sets(
    source_a: ComboSet,
    source_b: ComboSet,
) -> ComparisonResult:
    """
    Convenience function to compare two ComboSets.

    Args:
        source_a: First ComboSet
        source_b: Second ComboSet

    Returns:
        ComparisonResult
    """
    comparator = Comparator()
    return comparator.compare(source_a, source_b)
