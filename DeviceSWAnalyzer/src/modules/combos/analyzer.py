"""
Combos Module - Analyzer Implementation for Web UI

Implements BaseAnalyzer interface for auto-discovery by the module registry.
Integrates with the Flask web UI for file upload and analysis.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent path for imports
base_dir = Path(__file__).parent.parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from core.base_analyzer import BaseAnalyzer, InputFieldConfig, AnalysisInput, AnalysisResult

from .orchestrator import CombosOrchestrator
from .reports import PromptGenerator


class CombosAnalyzerModule(BaseAnalyzer):
    """
    CA/DC Combos Analysis Module

    Analyzes carrier aggregation and dual connectivity combinations
    from multiple sources to identify discrepancies.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the combos analyzer module."""
        self.output_dir = output_dir
        self._orchestrator: Optional[CombosOrchestrator] = None
        self._prompt_generator = PromptGenerator()

    @property
    def module_id(self) -> str:
        return "combos"

    @property
    def display_name(self) -> str:
        return "CA/DC Combos"

    @property
    def description(self) -> str:
        return ("Analyze Carrier Aggregation (CA) and Dual Connectivity (DC) "
                "combinations by comparing RFC definitions against built RRC "
                "tables and UE capability advertisements.")

    @property
    def icon(self) -> str:
        return "combos"

    @property
    def status(self) -> str:
        return "active"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_fields(self) -> List[InputFieldConfig]:
        """Define input fields for combo analysis."""
        return [
            InputFieldConfig(
                name="rfc_file",
                label="RFC XML",
                file_types=[".xml"],
                patterns=["*rfc*.xml", "*ca_combos*.xml", "*rf_card*.xml"],
                required=False,
                description="RFC XML file containing combo definitions"
            ),
            InputFieldConfig(
                name="qxdm_file",
                label="QXDM 0xB826 Log",
                file_types=[".txt", ".log"],
                patterns=["*0xb826*.txt", "*b826*.txt", "*qxdm*.txt", "*rrc*.txt"],
                required=False,
                description="QXDM text export of 0xB826 log packet"
            ),
            InputFieldConfig(
                name="uecap_file",
                label="UE Capability (P1)",
                file_types=[".xml", ".txt"],
                patterns=["*uecap*.xml", "*ue_cap*.xml", "*capability*.xml"],
                required=False,
                description="UE Capability data (Coming in P1)"
            ),
        ]

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        """Define optional parameters."""
        return [
            {
                "name": "carrier",
                "label": "Carrier (Optional)",
                "type": "text",
                "default": "",
                "description": "Target carrier for context (e.g., Verizon, AT&T)"
            },
            {
                "name": "region",
                "label": "Region (Optional)",
                "type": "select",
                "options": ["", "NA", "APAC", "EMEA", "LATAM"],
                "default": "",
                "description": "Target region for context"
            },
        ]

    @property
    def supports_ai_review(self) -> bool:
        return True

    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        """
        Run combo analysis on the provided inputs.

        Args:
            inputs: AnalysisInput containing file paths and parameters

        Returns:
            AnalysisResult with analysis outcome
        """
        # Initialize result
        result = AnalysisResult(
            success=False,
            module_id=self.module_id,
            timestamp=datetime.now(),
        )

        # Validate inputs
        errors = self.validate_inputs(inputs)
        if errors:
            result.errors = errors
            return result

        # Get file paths
        rfc_file = inputs.files.get("rfc_file")
        qxdm_file = inputs.files.get("qxdm_file")
        uecap_file = inputs.files.get("uecap_file")

        # Ensure at least one file is provided
        if not any([rfc_file, qxdm_file, uecap_file]):
            result.errors.append("At least one input file is required")
            return result

        # Determine output directory
        output_dir = self.output_dir
        if not output_dir:
            # Try to get from Flask config or use default
            output_dir = os.path.join(str(base_dir), 'output')
            os.makedirs(output_dir, exist_ok=True)

        try:
            # Create orchestrator
            self._orchestrator = CombosOrchestrator(output_dir=output_dir)

            # Run analysis
            response = self._orchestrator.analyze(
                rfc_file=rfc_file,
                qxdm_file=qxdm_file,
                uecap_file=uecap_file,
                generate_html=True,
                generate_prompt=True,
            )

            if response['success']:
                result.success = True
                result.html_report_path = response.get('html_path')
                result.prompt_path = response.get('prompt_path')

                # Generate CLI output summary
                analysis_result = response.get('result')
                if analysis_result:
                    result.summary = analysis_result.summary
                    result.details = {
                        'discrepancy_count': len(analysis_result.discrepancies),
                        'combo_counts': analysis_result.summary.get('total_combos', {}),
                        'comparisons': analysis_result.summary.get('comparisons', {}),
                    }
                    result.cli_output = self._generate_cli_output(analysis_result)
            else:
                result.errors.append(response.get('error', 'Unknown error'))

        except Exception as e:
            result.errors.append(f"Analysis error: {str(e)}")
            import traceback
            print(f"[ERROR] {traceback.format_exc()}", flush=True)

        return result

    def generate_prompt(self, result: AnalysisResult) -> str:
        """
        Generate a prompt for Claude AI review.

        Args:
            result: The analysis result to generate prompt for

        Returns:
            String prompt for Claude
        """
        if self._orchestrator and self._orchestrator.get_last_result():
            return self._prompt_generator.generate(self._orchestrator.get_last_result())

        # Fallback to basic prompt
        return f"""# Combos Analysis Review Request

## Summary
The combos analysis completed with the following results:
- Success: {result.success}
- Discrepancies found: {result.details.get('discrepancy_count', 0)}

Please review the attached HTML report for detailed analysis.
"""

    def generate_html_report(self, result: AnalysisResult, output_path: str) -> str:
        """
        Generate an HTML report.

        Note: HTML report is already generated by the orchestrator during analyze().
        This method is here for compatibility with the base class.
        """
        if result.html_report_path:
            return result.html_report_path

        # If no report exists, generate one
        if self._orchestrator:
            return self._orchestrator.regenerate_html(output_path)

        raise ValueError("No analysis result available to generate report from")

    def _generate_cli_output(self, analysis_result) -> str:
        """Generate CLI-style text output summary."""
        lines = [
            "=" * 60,
            "COMBOS ANALYSIS RESULTS",
            "=" * 60,
            "",
        ]

        summary = analysis_result.summary

        # Combo counts
        total = summary.get('total_combos', {})
        lines.append("COMBO COUNTS:")
        lines.append(f"  RFC:       {total.get('rfc', 0)}")
        lines.append(f"  RRC Table: {total.get('rrc', 0)}")
        lines.append(f"  UE Cap:    {total.get('uecap', 0)}")
        lines.append("")

        # By type
        by_type = summary.get('by_type', {})
        if by_type:
            lines.append("BY COMBO TYPE:")
            lines.append(f"  {'Type':<12} {'RFC':>8} {'RRC':>8} {'UE Cap':>8}")
            lines.append(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
            for ctype, counts in by_type.items():
                lines.append(f"  {ctype:<12} {counts.get('rfc', 0):>8} {counts.get('rrc', 0):>8} {counts.get('uecap', 0):>8}")
            lines.append("")

        # Comparison results
        comparisons = summary.get('comparisons', {})

        rfc_rrc = comparisons.get('rfc_vs_rrc', {})
        if rfc_rrc:
            lines.append("RFC vs RRC TABLE COMPARISON:")
            lines.append(f"  Match Rate:     {rfc_rrc.get('match_percentage', 0):.1f}%")
            lines.append(f"  Missing in RRC: {rfc_rrc.get('missing_in_rrc', 0)}")
            lines.append(f"  Extra in RRC:   {rfc_rrc.get('extra_in_rrc', 0)}")
            lines.append(f"  BCS Mismatches: {rfc_rrc.get('bcs_mismatches', 0)}")
            lines.append("")

        rrc_uecap = comparisons.get('rrc_vs_uecap', {})
        if rrc_uecap:
            lines.append("RRC TABLE vs UE CAPABILITY COMPARISON:")
            lines.append(f"  Match Rate:      {rrc_uecap.get('match_percentage', 0):.1f}%")
            lines.append(f"  Missing in UE Cap: {rrc_uecap.get('missing_in_uecap', 0)}")
            lines.append(f"  BCS Mismatches:  {rrc_uecap.get('bcs_mismatches', 0)}")
            lines.append("")

        # Total discrepancies
        total_disc = len(analysis_result.discrepancies)
        lines.append(f"TOTAL DISCREPANCIES: {total_disc}")

        if total_disc > 0:
            # Count by severity
            severity_counts = {}
            for disc in analysis_result.discrepancies:
                sev = disc.severity
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            lines.append("BY SEVERITY:")
            for sev in ['critical', 'high', 'medium', 'low', 'expected', 'unknown']:
                if sev in severity_counts:
                    lines.append(f"  {sev.upper()}: {severity_counts[sev]}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# Factory function for module discovery
def get_analyzer() -> BaseAnalyzer:
    """Get the combos analyzer instance for module discovery."""
    return CombosAnalyzerModule()
