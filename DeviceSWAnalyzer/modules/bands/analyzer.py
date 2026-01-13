"""
Bands Module Analyzer

Wraps the existing BandAnalyzer in the new plugin architecture.
"""

import sys
from io import StringIO
from pathlib import Path
from typing import List
from datetime import datetime

# Add parent paths for imports
base_dir = Path(__file__).parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from core.base_analyzer import (
    BaseAnalyzer,
    AnalysisInput,
    AnalysisResult,
    InputFieldConfig
)


class BandsModuleAnalyzer(BaseAnalyzer):
    """
    Band Analysis Module

    Analyzes modem band configurations from RFC XML, HW Filter,
    Carrier Policy, MCFG, MDB, QXDM logs, and UE Capability files.
    """

    @property
    def module_id(self) -> str:
        return "bands"

    @property
    def display_name(self) -> str:
        return "Band Analysis"

    @property
    def description(self) -> str:
        return "Analyze modem band configurations and filtering pipeline"

    @property
    def icon(self) -> str:
        return "signal"

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
                patterns=['*rfc*.xml'],
                required=False,
                description='RF Card capability file'
            ),
            InputFieldConfig(
                name='hw_filter_path',
                label='HW Filter XML',
                file_types=['.xml'],
                patterns=['*hardware*filter*.xml', '*hw*filter*.xml'],
                required=False,
                description='Hardware band filtering'
            ),
            InputFieldConfig(
                name='carrier_policy_path',
                label='Carrier Policy XML',
                file_types=['.xml'],
                patterns=['*carrier*policy*.xml'],
                required=False,
                description='Carrier-specific exclusions'
            ),
            InputFieldConfig(
                name='generic_restriction_path',
                label='Generic Restrictions XML',
                file_types=['.xml'],
                patterns=['*generic*.xml'],
                required=False,
                description='Generic band restrictions'
            ),
            InputFieldConfig(
                name='mcfg_path',
                label='MCFG XML',
                file_types=['.xml'],
                patterns=['*mcfg*.xml'],
                required=False,
                description='NV band preferences'
            ),
            InputFieldConfig(
                name='mdb_path',
                label='MDB XML',
                file_types=['.xml'],
                patterns=['*mcc2bands*.xml', '*mdb*.xml'],
                required=False,
                description='MCC to bands mapping'
            ),
            InputFieldConfig(
                name='qxdm_log_path',
                label='QXDM Log',
                file_types=['.txt'],
                patterns=['*qxdm*.txt', '*pm_rf*.txt', '*0x1cca*.txt', '*pm rf*.txt'],
                required=False,
                description='0x1CCA PM RF Band Info'
            ),
            InputFieldConfig(
                name='ue_capability_path',
                label='UE Capability',
                file_types=['.txt'],
                patterns=['*ue_cap*.txt', '*capability*.txt', '*ue cap*.txt'],
                required=False,
                description='UE Capability Information'
            ),
        ]

    @property
    def parameters(self) -> List[dict]:
        return [
            {
                'name': 'target_mcc',
                'type': 'text',
                'label': 'Target MCC',
                'placeholder': 'e.g., 310',
                'required': False,
                'description': 'MCC for MDB lookup'
            }
        ]

    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        """Run band analysis."""
        from src.core.analyzer import BandAnalyzer, AnalysisInput as LegacyInput
        from src.output.html_report import generate_html_report
        from src.output.console_report import print_console_report
        from src.core.prompt_generator import generate_prompt

        cli_output = ""
        errors = []

        try:
            # Create legacy input format
            legacy_inputs = LegacyInput(
                rfc_path=inputs.files.get('rfc_path'),
                hw_filter_path=inputs.files.get('hw_filter_path'),
                carrier_policy_path=inputs.files.get('carrier_policy_path'),
                generic_restriction_path=inputs.files.get('generic_restriction_path'),
                mcfg_path=inputs.files.get('mcfg_path'),
                mdb_path=inputs.files.get('mdb_path'),
                qxdm_log_path=inputs.files.get('qxdm_log_path'),
                ue_capability_path=inputs.files.get('ue_capability_path'),
                target_mcc=inputs.parameters.get('target_mcc')
            )

            # Capture CLI output
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                # Run analysis
                analyzer = BandAnalyzer()
                result = analyzer.analyze(legacy_inputs)

                # Print console report
                print_console_report(result)

            finally:
                sys.stdout = old_stdout
                cli_output = captured_output.getvalue()

            # Generate timestamp for filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Generate HTML report
            html_filename = f'band_analysis_{timestamp}.html'
            html_report_path = str(base_dir / 'output' / html_filename)
            generate_html_report(result, html_report_path)

            # Generate prompt file
            prompt_filename = f'prompt_{timestamp}.txt'
            prompt_path = str(base_dir / 'output' / prompt_filename)
            generate_prompt(result, output_path=prompt_path)

            # Create summary
            summary = {
                'gsm_bands': len(result.gsm_bands) if hasattr(result, 'gsm_bands') else 0,
                'wcdma_bands': len(result.wcdma_bands) if hasattr(result, 'wcdma_bands') else 0,
                'lte_bands': len(result.lte_bands) if hasattr(result, 'lte_bands') else 0,
                'nr_sa_bands': len(result.nr_sa_bands) if hasattr(result, 'nr_sa_bands') else 0,
                'nr_nsa_bands': len(result.nr_nsa_bands) if hasattr(result, 'nr_nsa_bands') else 0,
            }

            return AnalysisResult(
                success=True,
                module_id=self.module_id,
                summary=summary,
                details={'legacy_result': result},
                cli_output=cli_output,
                html_report_path=html_report_path,
                prompt_path=prompt_path,
                errors=errors
            )

        except Exception as e:
            import traceback
            error_msg = f"Error during analysis: {str(e)}"
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
        from src.core.prompt_generator import generate_prompt

        if result.details and 'legacy_result' in result.details:
            return generate_prompt(result.details['legacy_result'])
        return ""

    def generate_html_report(self, result: AnalysisResult, output_path: str) -> str:
        """Generate HTML report."""
        from src.output.html_report import generate_html_report

        if result.details and 'legacy_result' in result.details:
            generate_html_report(result.details['legacy_result'], output_path)
        return output_path
