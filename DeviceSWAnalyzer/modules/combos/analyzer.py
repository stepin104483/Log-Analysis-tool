"""
Combos Analysis Module (CA, EN-DC)

Analyzes carrier aggregation and EN-DC combinations.
Status: Active
"""

import sys
from pathlib import Path
from typing import List
from datetime import datetime

# Add parent paths for imports
base_dir = Path(__file__).parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

src_dir = base_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.base_analyzer import (
    BaseAnalyzer,
    AnalysisInput,
    AnalysisResult,
    InputFieldConfig
)


class CombosModuleAnalyzer(BaseAnalyzer):
    """
    Combos (CA, EN-DC) Analysis Module

    Analyzes carrier aggregation combinations and EN-DC configurations
    by comparing RFC, QXDM (0xB826), and UE Capability data sources.
    """

    @property
    def module_id(self) -> str:
        return "combos"

    @property
    def display_name(self) -> str:
        return "Combos (CA, ENDC)"

    @property
    def description(self) -> str:
        return "Analyze carrier aggregation and EN-DC combinations"

    @property
    def icon(self) -> str:
        return "layers"

    @property
    def status(self) -> str:
        return "active"

    @property
    def input_fields(self) -> List[InputFieldConfig]:
        return [
            InputFieldConfig(
                name='rfc_path',
                label='RFC XML',
                file_types=['.xml'],
                patterns=['*rfc*.xml', '*RFC*.xml'],
                required=False,
                description='RF Card capability file with combo definitions'
            ),
            InputFieldConfig(
                name='qxdm_path',
                label='QXDM 0xB826 Log',
                file_types=['.txt', '.log'],
                patterns=['*0xb826*.txt', '*0xB826*.txt', '*rrc*.txt', '*combo*.txt'],
                required=False,
                description='QXDM 0xB826 RRC combo table output'
            ),
            InputFieldConfig(
                name='uecap_path',
                label='UE Capability',
                file_types=['.xml', '.txt'],
                patterns=['*uecap*.xml', '*uecap*.txt', '*capability*.xml', '*capability*.txt', '*UE_Cap*.*'],
                required=False,
                description='UE Capability ASN.1 XML or text export'
            ),
        ]

    @property
    def parameters(self) -> List[dict]:
        # No additional parameters needed for basic combo analysis
        return []

    @property
    def supports_ai_review(self) -> bool:
        return True

    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        """Run combos analysis."""
        from src.modules.combos import CombosOrchestrator

        cli_output = ""
        errors = []

        try:
            # Get file paths
            rfc_path = inputs.files.get('rfc_path')
            qxdm_path = inputs.files.get('qxdm_path')
            uecap_path = inputs.files.get('uecap_path')

            # Validate at least one input
            if not any([rfc_path, qxdm_path, uecap_path]):
                return AnalysisResult(
                    success=False,
                    module_id=self.module_id,
                    cli_output="Error: At least one input file (RFC, QXDM, or UE Capability) is required.",
                    errors=["No input files provided"]
                )

            # Set up output directory
            output_dir = base_dir / 'output'
            output_dir.mkdir(exist_ok=True)

            # Run analysis using orchestrator
            orchestrator = CombosOrchestrator(output_dir=str(output_dir))

            # orchestrator.analyze() returns a dict with keys:
            # 'success', 'result', 'html_path', 'prompt_path', 'error'
            response = orchestrator.analyze(
                rfc_file=rfc_path,
                qxdm_file=qxdm_path,
                uecap_file=uecap_path,
            )

            # Check if analysis succeeded
            if not response.get('success'):
                error_msg = response.get('error', 'Unknown error during analysis')
                return AnalysisResult(
                    success=False,
                    module_id=self.module_id,
                    cli_output=f"Analysis failed: {error_msg}",
                    errors=[error_msg]
                )

            # Get the actual analysis result object
            analysis_result = response.get('result')
            if not analysis_result:
                return AnalysisResult(
                    success=False,
                    module_id=self.module_id,
                    cli_output="Analysis completed but no result returned",
                    errors=["No analysis result"]
                )

            # Build CLI output summary
            cli_lines = []
            cli_lines.append("=" * 60)
            cli_lines.append("COMBOS ANALYSIS RESULTS")
            cli_lines.append("=" * 60)
            cli_lines.append("")

            # Input files
            cli_lines.append("INPUT FILES:")
            if rfc_path:
                cli_lines.append(f"  RFC: {Path(rfc_path).name}")
            if qxdm_path:
                cli_lines.append(f"  QXDM: {Path(qxdm_path).name}")
            if uecap_path:
                cli_lines.append(f"  UE Cap: {Path(uecap_path).name}")
            cli_lines.append("")

            # Summary stats from the analysis result object
            summary = analysis_result.summary if hasattr(analysis_result, 'summary') else {}
            total_combos = summary.get('total_combos', {})
            cli_lines.append("COMBO COUNTS:")
            cli_lines.append(f"  RFC:     {total_combos.get('rfc', 0)}")
            cli_lines.append(f"  RRC:     {total_combos.get('rrc', 0)}")
            cli_lines.append(f"  UE Cap:  {total_combos.get('uecap', 0)}")
            cli_lines.append("")

            # Discrepancies
            discrepancies = analysis_result.discrepancies if hasattr(analysis_result, 'discrepancies') else []
            total_disc = len(discrepancies)
            cli_lines.append(f"DISCREPANCIES: {total_disc}")

            if total_disc > 0:
                # Count by severity
                severity_counts = {}
                for d in discrepancies:
                    sev = getattr(d, 'severity', 'unknown') or 'unknown'
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                for sev in ['critical', 'high', 'medium', 'low', 'expected']:
                    if sev in severity_counts:
                        cli_lines.append(f"  {sev.upper()}: {severity_counts[sev]}")

            cli_lines.append("")
            cli_lines.append("=" * 60)

            cli_output = "\n".join(cli_lines)

            # Get report paths from orchestrator response
            html_report_path = response.get('html_path')
            prompt_path = response.get('prompt_path')

            # Create summary for result
            result_summary = {
                'rfc_combos': total_combos.get('rfc', 0),
                'rrc_combos': total_combos.get('rrc', 0),
                'uecap_combos': total_combos.get('uecap', 0),
                'total_discrepancies': total_disc,
                'by_type': summary.get('by_type', {}),
            }

            return AnalysisResult(
                success=True,
                module_id=self.module_id,
                summary=result_summary,
                details={'combos_result': analysis_result},
                cli_output=cli_output,
                html_report_path=html_report_path,
                prompt_path=prompt_path,
                errors=errors
            )

        except Exception as e:
            import traceback
            error_msg = f"Error during combos analysis: {str(e)}"
            cli_output = f"{error_msg}\n{traceback.format_exc()}"
            errors.append(error_msg)

            return AnalysisResult(
                success=False,
                module_id=self.module_id,
                cli_output=cli_output,
                errors=errors
            )

    def generate_prompt(self, result: AnalysisResult) -> str:
        """Generate Claude prompt for this analysis."""
        from src.modules.combos.reports import PromptGenerator

        if result.details and 'combos_result' in result.details:
            generator = PromptGenerator()
            return generator.generate(result.details['combos_result'])
        return ""

    def generate_html_report(self, result: AnalysisResult, output_path: str) -> str:
        """Generate HTML report."""
        from src.modules.combos.reports import HTMLReportGenerator

        if result.details and 'combos_result' in result.details:
            generator = HTMLReportGenerator()
            generator.generate(result.details['combos_result'], output_path)
        return output_path
