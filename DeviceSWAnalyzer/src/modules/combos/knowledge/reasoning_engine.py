"""
Reasoning Engine

Provides explanations for WHY discrepancies exist using knowledge base context.
This engine does NOT filter combos - it only provides context and reasoning.

Severity levels:
- expected: Known restriction, no action needed
- low: Minor, informational only
- medium: Should be reviewed
- high: Potential configuration error
- critical: Likely bug or serious misconfiguration
"""

import logging
from typing import Dict, List, Optional, Set

from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    Discrepancy,
    ReasoningResult,
    KnowledgeBaseContext,
    BandRestriction,
    ComboRestriction,
)

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Reasoning engine that explains WHY discrepancies exist.

    Uses knowledge base context to provide explanations for discrepancies
    found during combo analysis. Does NOT filter - only explains.
    """

    def __init__(self, knowledge_base: Optional[KnowledgeBaseContext] = None):
        """
        Initialize reasoning engine.

        Args:
            knowledge_base: Optional KnowledgeBaseContext with loaded rules
        """
        self.kb = knowledge_base or KnowledgeBaseContext()

    def set_knowledge_base(self, kb: KnowledgeBaseContext):
        """Set or update the knowledge base context."""
        self.kb = kb

    def explain_discrepancy(self, discrepancy: Discrepancy) -> ReasoningResult:
        """
        Attempt to explain why a discrepancy exists.

        Checks in order:
        1. EFS pruning (if PRUNED_BY_EFS type)
        2. Band restrictions (is any band in combo restricted?)
        3. Combo restrictions (is this specific combo restricted?)
        4. Carrier requirements (does carrier exclude/require this?)
        5. Return "unknown" if no explanation found

        Args:
            discrepancy: The discrepancy to explain

        Returns:
            ReasoningResult with explanation or "unknown"
        """
        # Handle EFS pruning discrepancies
        if discrepancy.discrepancy_type == DiscrepancyType.PRUNED_BY_EFS:
            return self._explain_efs_pruning(discrepancy)

        # Handle envelope filtering
        if discrepancy.discrepancy_type == DiscrepancyType.ENVELOPE_FILTERED:
            return self._explain_envelope_filtering(discrepancy)

        # Extract bands from combo
        bands = [c.band for c in discrepancy.combo.components]
        nr_bands = [c.band for c in discrepancy.combo.components if c.is_nr]
        lte_bands = [c.band for c in discrepancy.combo.components if not c.is_nr]

        # Step 1: Check band restrictions
        for band in bands:
            if band in self.kb.band_restrictions:
                restrictions = self.kb.band_restrictions[band]
                for r in restrictions:
                    if self._restriction_applies(r):
                        return ReasoningResult(
                            has_explanation=True,
                            reason_type=r.restriction_type,
                            explanation=f"Band {band}: {r.reason}",
                            source_file=r.source_file,
                            severity=self._calculate_severity_for_band_restriction(r, discrepancy),
                            recommended_action=self._get_recommendation_for_band_restriction(r),
                        )

        # Step 2: Check combo restrictions
        combo_key = discrepancy.combo.normalized_key
        if combo_key in self.kb.combo_restrictions:
            restrictions = self.kb.combo_restrictions[combo_key]
            if restrictions:
                r = restrictions[0]
                return ReasoningResult(
                    has_explanation=True,
                    reason_type=r.restriction_type,
                    explanation=r.reason or f"Combo {combo_key} is restricted",
                    source_file=r.source_file,
                    severity="expected",
                    recommended_action="No action - expected restriction",
                )

        # Step 3: Check carrier requirements
        if self.kb.active_carrier:
            carrier_key = self.kb.active_carrier.lower()
            if carrier_key in self.kb.carrier_requirements:
                carrier_req = self.kb.carrier_requirements[carrier_key]

                # Check if combo is excluded
                if combo_key in carrier_req.excluded_combos:
                    note = carrier_req.notes.get(combo_key, '')
                    return ReasoningResult(
                        has_explanation=True,
                        reason_type="carrier",
                        explanation=f"Excluded by {self.kb.active_carrier} policy" +
                                   (f": {note}" if note else ""),
                        source_file=f"{carrier_key}.yaml",
                        severity="expected",
                        recommended_action="No action - carrier exclusion",
                    )

                # Check if combo is required but missing
                if (discrepancy.discrepancy_type == DiscrepancyType.MISSING_IN_RRC and
                    combo_key in carrier_req.required_combos):
                    return ReasoningResult(
                        has_explanation=True,
                        reason_type="carrier",
                        explanation=f"Required by {self.kb.active_carrier} but missing in RRC",
                        source_file=f"{carrier_key}.yaml",
                        severity="critical",
                        recommended_action="Investigate - required combo is missing",
                    )

        # Step 4: Apply heuristics based on discrepancy type
        return self._apply_heuristics(discrepancy)

    def _explain_efs_pruning(self, discrepancy: Discrepancy) -> ReasoningResult:
        """Explain EFS pruning discrepancy."""
        return ReasoningResult(
            has_explanation=True,
            reason_type="efs",
            explanation="Combo disabled by EFS pruning configuration",
            source_file=discrepancy.details or "prune_ca_combos",
            severity="expected",
            recommended_action="No action - intentionally pruned by EFS",
        )

    def _explain_envelope_filtering(self, discrepancy: Discrepancy) -> ReasoningResult:
        """Explain RF envelope filtering discrepancy."""
        return ReasoningResult(
            has_explanation=True,
            reason_type="envelope",
            explanation="Combo filtered by RF envelope validation",
            source_file="RFPD envelope",
            severity="expected",
            recommended_action="No action - RF envelope constraint",
        )

    def _restriction_applies(self, restriction: BandRestriction) -> bool:
        """Check if a restriction applies to the current context."""
        # If no regions specified, restriction always applies
        if not restriction.regions:
            return True

        # If active region is set, check if it matches
        if self.kb.active_region:
            return self.kb.active_region.upper() in [r.upper() for r in restriction.regions]

        # If no active region, consider restriction as applicable
        return True

    def _calculate_severity_for_band_restriction(
        self,
        restriction: BandRestriction,
        discrepancy: Discrepancy
    ) -> str:
        """Calculate severity based on restriction type and discrepancy."""
        severity_map = {
            "regional": "expected",
            "regulatory": "expected",
            "hw_variant": "low",
            "carrier": "expected",
        }

        base_severity = severity_map.get(restriction.restriction_type, "medium")

        # Elevate severity for certain discrepancy types
        if discrepancy.discrepancy_type == DiscrepancyType.EXTRA_IN_RRC:
            # Extra combos in RRC that are restricted could be a config issue
            if base_severity == "expected":
                return "low"
            return "medium"

        return base_severity

    def _get_recommendation_for_band_restriction(self, restriction: BandRestriction) -> str:
        """Generate recommendation based on restriction type."""
        recommendations = {
            "regional": "No action - regional restriction as designed",
            "regulatory": "No action - regulatory compliance requirement",
            "hw_variant": "Verify hardware variant matches build configuration",
            "carrier": "Verify carrier requirements are current",
        }
        return recommendations.get(
            restriction.restriction_type,
            "Review manually - restriction type unknown"
        )

    def _apply_heuristics(self, discrepancy: Discrepancy) -> ReasoningResult:
        """
        Apply heuristics when no knowledge base match is found.

        Uses patterns and common scenarios to provide likely explanations.
        """
        combo = discrepancy.combo
        disc_type = discrepancy.discrepancy_type

        # Heuristic 1: High band numbers (mmWave) often have regional restrictions
        nr_bands = [c.band for c in combo.components if c.is_nr]
        if any(b >= 257 for b in nr_bands):
            if disc_type == DiscrepancyType.MISSING_IN_RRC:
                return ReasoningResult(
                    has_explanation=True,
                    reason_type="heuristic",
                    explanation="mmWave band combo - may have regional/HW restrictions",
                    severity="low",
                    recommended_action="Verify mmWave support for target market",
                )

        # Heuristic 2: Band 14 (FirstNet) is US-only
        if 14 in [c.band for c in combo.components]:
            return ReasoningResult(
                has_explanation=True,
                reason_type="heuristic",
                explanation="Band 14 (FirstNet) - US regulatory restriction",
                severity="expected" if self.kb.active_region != "NA" else "medium",
                recommended_action="No action if non-US market",
            )

        # Heuristic 3: Band 71 (T-Mobile) often excluded for non-T-Mobile builds
        if 71 in [c.band for c in combo.components]:
            return ReasoningResult(
                has_explanation=True,
                reason_type="heuristic",
                explanation="Band 71 - often carrier-specific (T-Mobile US)",
                severity="low",
                recommended_action="Verify carrier requirements",
            )

        # Heuristic 4: BCS mismatch often due to version differences
        if disc_type == DiscrepancyType.BCS_MISMATCH:
            return ReasoningResult(
                has_explanation=True,
                reason_type="heuristic",
                explanation="BCS mismatch - may indicate version or configuration difference",
                severity="medium",
                recommended_action="Review BCS configuration in RFC",
            )

        # Heuristic 5: Extra in RRC might be dynamic addition
        if disc_type == DiscrepancyType.EXTRA_IN_RRC:
            return ReasoningResult(
                has_explanation=True,
                reason_type="heuristic",
                explanation="Combo in RRC but not RFC - may be dynamically added or from different RFC version",
                severity="medium",
                recommended_action="Verify RFC version matches build",
            )

        # No explanation found
        return ReasoningResult(
            has_explanation=False,
            reason_type=None,
            explanation=None,
            severity=self._default_severity(disc_type),
            recommended_action="Investigate - unexpected discrepancy",
        )

    def _default_severity(self, disc_type: DiscrepancyType) -> str:
        """Get default severity based on discrepancy type."""
        severity_defaults = {
            DiscrepancyType.MISSING_IN_RRC: "high",
            DiscrepancyType.MISSING_IN_UECAP: "high",
            DiscrepancyType.EXTRA_IN_RRC: "medium",
            DiscrepancyType.BCS_MISMATCH: "medium",
            DiscrepancyType.PRUNED_BY_EFS: "expected",
            DiscrepancyType.ENVELOPE_FILTERED: "expected",
        }
        return severity_defaults.get(disc_type, "medium")

    def enrich_discrepancies(self, discrepancies: List[Discrepancy]) -> List[Discrepancy]:
        """
        Add reasoning to all discrepancies.

        Args:
            discrepancies: List of discrepancies to enrich

        Returns:
            Same list with reasoning added to each discrepancy
        """
        for d in discrepancies:
            if d.reason is None:
                d.reason = self.explain_discrepancy(d)

        return discrepancies

    def categorize_by_severity(
        self,
        discrepancies: List[Discrepancy]
    ) -> Dict[str, List[Discrepancy]]:
        """
        Categorize discrepancies by severity level.

        Args:
            discrepancies: List of discrepancies (should be enriched first)

        Returns:
            Dict mapping severity to list of discrepancies
        """
        result = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'expected': [],
            'unknown': [],
        }

        for d in discrepancies:
            severity = d.severity
            if severity in result:
                result[severity].append(d)
            else:
                result['unknown'].append(d)

        return result

    def get_action_items(self, discrepancies: List[Discrepancy]) -> List[Dict]:
        """
        Get prioritized action items from discrepancies.

        Args:
            discrepancies: List of enriched discrepancies

        Returns:
            List of action items sorted by priority
        """
        actions = []

        for d in discrepancies:
            if d.severity in ['critical', 'high']:
                action = {
                    'combo': str(d.combo),
                    'severity': d.severity,
                    'type': d.discrepancy_type.name,
                    'action': d.reason.recommended_action if d.reason else "Investigate",
                    'explanation': d.reason.explanation if d.reason else None,
                }
                actions.append(action)

        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'high': 1}
        actions.sort(key=lambda x: severity_order.get(x['severity'], 2))

        return actions
