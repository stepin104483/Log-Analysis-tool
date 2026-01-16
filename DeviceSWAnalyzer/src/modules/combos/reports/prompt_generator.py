"""
Prompt Generator for AI Expert Review

Generates structured prompts for Claude to analyze combo discrepancies
and provide expert-level insights.
"""

from typing import Dict, List, Optional
from datetime import datetime

from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    Discrepancy,
    AnalysisResult,
)


class PromptGenerator:
    """Generate prompts for AI analysis of combo discrepancies."""

    def __init__(self):
        self.max_discrepancies_per_type = 50  # Limit to avoid token overflow

    def generate(self, result: AnalysisResult) -> str:
        """
        Generate analysis prompt from AnalysisResult.

        Args:
            result: AnalysisResult from CombosAnalyzer

        Returns:
            Formatted prompt string for AI review
        """
        sections = [
            self._build_header(),
            self._build_context_section(result),
            self._build_summary_section(result),
            self._build_discrepancies_section(result),
            self._build_analysis_request(),
        ]

        return "\n\n".join(sections)

    def generate_file(self, result: AnalysisResult, output_path: str) -> str:
        """
        Generate prompt and save to file.

        Args:
            result: AnalysisResult from CombosAnalyzer
            output_path: Path to save prompt file

        Returns:
            Path to saved file
        """
        prompt = self.generate(result)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)

        return output_path

    def _build_header(self) -> str:
        """Build prompt header with role and context."""
        return """# CA/DC Combo Analysis - Expert Review Request

You are a telecommunications expert specializing in LTE/NR carrier aggregation and dual connectivity configurations. You are reviewing a combo analysis report that compares:
- **RFC**: Expected combo definitions from RF Card configuration
- **RRC Table (0xB826)**: Actually built combos in the modem's RRC table
- **UE Capability**: Combos advertised to the network

Your task is to analyze the discrepancies found and provide expert insights on:
1. Root cause analysis for each category of discrepancy
2. Severity assessment and prioritization
3. Recommended actions for resolution
4. Any patterns or systemic issues observed"""

    def _build_context_section(self, result: AnalysisResult) -> str:
        """Build context section with file info and timestamps."""
        lines = ["## Analysis Context"]

        lines.append(f"\n**Timestamp:** {result.timestamp}")

        if result.input_files:
            lines.append("\n**Input Files:**")
            for source, filename in result.input_files.items():
                lines.append(f"- {source.upper()}: `{filename}`")

        # Unique bands
        if result.summary.get('unique_bands'):
            lte_bands = result.summary['unique_bands'].get('lte', [])
            nr_bands = result.summary['unique_bands'].get('nr', [])
            if lte_bands:
                lines.append(f"\n**LTE Bands:** {', '.join(map(str, sorted(lte_bands)))}")
            if nr_bands:
                lines.append(f"**NR Bands:** {', '.join(map(str, sorted(nr_bands)))}")

        return "\n".join(lines)

    def _build_summary_section(self, result: AnalysisResult) -> str:
        """Build summary statistics section."""
        summary = result.summary
        lines = ["## Summary Statistics"]

        # Combo counts
        total = summary.get('total_combos', {})
        lines.append(f"""
**Combo Counts:**
| Source | Count |
|--------|-------|
| RFC | {total.get('rfc', 0)} |
| RRC Table | {total.get('rrc', 0)} |
| UE Capability | {total.get('uecap', 0)} |
""")

        # By type breakdown
        by_type = summary.get('by_type', {})
        if by_type:
            lines.append("**By Combo Type:**")
            lines.append("| Type | RFC | RRC | UE Cap |")
            lines.append("|------|-----|-----|--------|")
            for combo_type in ComboType:
                type_data = by_type.get(combo_type.name, {})
                lines.append(f"| {combo_type.name} | {type_data.get('rfc', 0)} | {type_data.get('rrc', 0)} | {type_data.get('uecap', 0)} |")

        # Comparison results
        comparisons = summary.get('comparisons', {})

        rfc_rrc = comparisons.get('rfc_vs_rrc', {})
        if rfc_rrc:
            lines.append(f"""
**RFC vs RRC Table:**
- Match Rate: {rfc_rrc.get('match_percentage', 0):.1f}%
- Missing in RRC: {rfc_rrc.get('missing_in_rrc', 0)}
- Extra in RRC: {rfc_rrc.get('extra_in_rrc', 0)}
- BCS Mismatches: {rfc_rrc.get('bcs_mismatches', 0)}
""")

        rrc_uecap = comparisons.get('rrc_vs_uecap', {})
        if rrc_uecap:
            lines.append(f"""
**RRC Table vs UE Capability:**
- Match Rate: {rrc_uecap.get('match_percentage', 0):.1f}%
- Missing in UE Cap: {rrc_uecap.get('missing_in_uecap', 0)}
- BCS Mismatches: {rrc_uecap.get('bcs_mismatches', 0)}
""")

        return "\n".join(lines)

    def _build_discrepancies_section(self, result: AnalysisResult) -> str:
        """Build detailed discrepancies section."""
        lines = ["## Discrepancies Found"]

        if not result.discrepancies:
            lines.append("\nNo discrepancies found. All combos match across sources.")
            return "\n".join(lines)

        # Group by type
        by_type: Dict[DiscrepancyType, List[Discrepancy]] = {}
        for disc in result.discrepancies:
            if disc.discrepancy_type not in by_type:
                by_type[disc.discrepancy_type] = []
            by_type[disc.discrepancy_type].append(disc)

        for disc_type, discrepancies in by_type.items():
            lines.append(f"\n### {disc_type.name} ({len(discrepancies)} total)")

            # Describe the discrepancy type
            type_descriptions = {
                DiscrepancyType.MISSING_IN_RRC: "Combos defined in RFC but not found in the built RRC table",
                DiscrepancyType.EXTRA_IN_RRC: "Combos in RRC table that are not defined in RFC",
                DiscrepancyType.MISSING_IN_UECAP: "Combos in RRC table but not advertised in UE Capability",
                DiscrepancyType.BCS_MISMATCH: "Combos exist in both sources but have different BCS values",
                DiscrepancyType.PRUNED_BY_EFS: "Combos disabled by EFS configuration files",
                DiscrepancyType.ENVELOPE_FILTERED: "Combos filtered out by RF envelope validation",
            }
            lines.append(f"\n*{type_descriptions.get(disc_type, 'Unknown discrepancy type')}*")

            # Group by combo type for better organization
            by_combo_type: Dict[ComboType, List[Discrepancy]] = {}
            for disc in discrepancies:
                ctype = disc.combo.combo_type
                if ctype not in by_combo_type:
                    by_combo_type[ctype] = []
                by_combo_type[ctype].append(disc)

            for combo_type, type_discs in by_combo_type.items():
                lines.append(f"\n**{combo_type.name}:**")

                # Limit output
                limited = type_discs[:self.max_discrepancies_per_type]
                combo_strings = [str(d.combo) for d in limited]

                lines.append("```")
                lines.append("\n".join(combo_strings))
                if len(type_discs) > self.max_discrepancies_per_type:
                    lines.append(f"... and {len(type_discs) - self.max_discrepancies_per_type} more")
                lines.append("```")

        return "\n".join(lines)

    def _build_analysis_request(self) -> str:
        """Build the analysis request section."""
        return """## Analysis Request

Please provide your expert analysis addressing:

### 1. Root Cause Analysis
For each category of discrepancy, what are the likely root causes?
- Consider: EFS pruning, regional restrictions, hardware variants, regulatory requirements, build configuration issues

### 2. Severity Assessment
Prioritize the discrepancies by severity:
- **CRITICAL**: Combos missing that will cause user-visible issues (dropped calls, no connectivity)
- **HIGH**: Important combos missing that affect coverage or throughput
- **MEDIUM**: Nice-to-have combos missing, limited user impact
- **LOW**: Expected differences (known restrictions, regional variants)
- **EXPECTED**: Intentional filtering (EFS prune, carrier policy)

### 3. Recommended Actions
What specific actions should be taken to resolve the discrepancies?

### 4. Patterns Observed
Are there any systemic patterns or issues that suggest broader configuration problems?

### 5. Additional Notes
Any other observations or recommendations for the engineering team?

---
Please format your response in markdown with clear sections for each analysis area."""


def generate_prompt(result: AnalysisResult) -> str:
    """
    Convenience function to generate analysis prompt.

    Args:
        result: AnalysisResult from CombosAnalyzer

    Returns:
        Formatted prompt string
    """
    generator = PromptGenerator()
    return generator.generate(result)
