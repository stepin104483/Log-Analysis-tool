"""
Combos Orchestrator - High-Level Analysis API

Provides a simple, high-level API for running combo analysis:
- Single entry point for all analysis operations
- File handling and validation
- Report generation (HTML and prompt)
- Error handling and logging
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from .models import AnalysisResult, ComboType
from .analyzers import CombosAnalyzer
from .reports import HTMLReportGenerator, PromptGenerator

logger = logging.getLogger(__name__)


class CombosOrchestrator:
    """
    High-level orchestrator for combo analysis workflow.

    Provides a simple interface for:
    1. Validating input files
    2. Running analysis
    3. Generating reports (HTML + prompt)
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize orchestrator.

        Args:
            output_dir: Directory for output files (default: current dir)
        """
        self.output_dir = output_dir or os.getcwd()
        self.analyzer = CombosAnalyzer()
        self.html_generator = HTMLReportGenerator()
        self.prompt_generator = PromptGenerator()

        # Analysis state
        self._last_result: Optional[AnalysisResult] = None
        self._last_error: Optional[str] = None

    def analyze(
        self,
        rfc_file: Optional[str] = None,
        qxdm_file: Optional[str] = None,
        uecap_file: Optional[str] = None,
        generate_html: bool = True,
        generate_prompt: bool = True,
    ) -> Dict[str, Any]:
        """
        Run complete analysis workflow.

        Args:
            rfc_file: Path to RFC XML file
            qxdm_file: Path to QXDM 0xB826 text export
            uecap_file: Path to UE Capability data
            generate_html: Generate HTML report
            generate_prompt: Generate AI prompt file

        Returns:
            Dict with:
                - success: bool
                - result: AnalysisResult (if successful)
                - html_path: Path to HTML report (if generated)
                - prompt_path: Path to prompt file (if generated)
                - error: Error message (if failed)
        """
        self._last_error = None
        response = {
            'success': False,
            'result': None,
            'html_path': None,
            'prompt_path': None,
            'html_filename': None,
            'prompt_filename': None,
            'error': None,
        }

        try:
            # Validate inputs
            validation = self._validate_inputs(rfc_file, qxdm_file, uecap_file)
            if not validation['valid']:
                response['error'] = validation['error']
                self._last_error = validation['error']
                return response

            logger.info("Starting combo analysis...")

            # Run analysis
            result = self.analyzer.analyze(
                rfc_file=rfc_file,
                qxdm_file=qxdm_file,
                uecap_file=uecap_file,
            )

            self._last_result = result
            response['result'] = result
            response['success'] = True

            # Generate timestamp for filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Generate HTML report
            if generate_html:
                html_filename = f'combos_analysis_{timestamp}.html'
                html_path = os.path.join(self.output_dir, html_filename)
                self.html_generator.generate(result, html_path)
                response['html_path'] = html_path
                response['html_filename'] = html_filename
                logger.info(f"Generated HTML report: {html_path}")

            # Generate prompt file
            if generate_prompt:
                prompt_filename = f'combos_prompt_{timestamp}.txt'
                prompt_path = os.path.join(self.output_dir, prompt_filename)
                self.prompt_generator.generate_file(result, prompt_path)
                response['prompt_path'] = prompt_path
                response['prompt_filename'] = prompt_filename
                logger.info(f"Generated prompt file: {prompt_path}")

            logger.info("Combo analysis completed successfully")

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.exception(error_msg)
            response['error'] = error_msg
            self._last_error = error_msg

        return response

    def _validate_inputs(
        self,
        rfc_file: Optional[str],
        qxdm_file: Optional[str],
        uecap_file: Optional[str],
    ) -> Dict[str, Any]:
        """
        Validate input files.

        Args:
            rfc_file: RFC XML file path
            qxdm_file: QXDM file path
            uecap_file: UE Cap file path

        Returns:
            Dict with 'valid' bool and optional 'error' message
        """
        # At least one file required
        if not any([rfc_file, qxdm_file, uecap_file]):
            return {
                'valid': False,
                'error': 'At least one input file is required'
            }

        # Validate file existence
        for file_path, name in [
            (rfc_file, 'RFC'),
            (qxdm_file, 'QXDM'),
            (uecap_file, 'UE Capability'),
        ]:
            if file_path and not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': f'{name} file not found: {file_path}'
                }

        # For comparison, need at least two sources
        source_count = sum([
            1 if rfc_file else 0,
            1 if qxdm_file else 0,
            1 if uecap_file else 0,
        ])

        if source_count < 2:
            logger.warning("Only one source provided - no comparison possible")

        return {'valid': True}

    def get_last_result(self) -> Optional[AnalysisResult]:
        """Get the result from the last analysis run."""
        return self._last_result

    def get_last_error(self) -> Optional[str]:
        """Get the error from the last analysis run."""
        return self._last_error

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of last analysis.

        Returns:
            Summary dict or empty dict if no analysis run
        """
        if not self._last_result:
            return {}

        return self._last_result.summary

    def get_discrepancy_count(self) -> int:
        """Get total discrepancy count from last analysis."""
        if not self._last_result:
            return 0
        return len(self._last_result.discrepancies)

    def regenerate_html(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Regenerate HTML report from last analysis.

        Args:
            output_path: Custom output path (optional)

        Returns:
            Path to generated HTML or None if no result
        """
        if not self._last_result:
            return None

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f'combos_analysis_{timestamp}.html')

        self.html_generator.generate(self._last_result, output_path)
        return output_path

    def regenerate_prompt(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Regenerate prompt file from last analysis.

        Args:
            output_path: Custom output path (optional)

        Returns:
            Path to generated prompt or None if no result
        """
        if not self._last_result:
            return None

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f'combos_prompt_{timestamp}.txt')

        self.prompt_generator.generate_file(self._last_result, output_path)
        return output_path


def run_analysis(
    rfc_file: Optional[str] = None,
    qxdm_file: Optional[str] = None,
    uecap_file: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to run combo analysis.

    Args:
        rfc_file: Path to RFC XML file
        qxdm_file: Path to QXDM 0xB826 text export
        uecap_file: Path to UE Capability data
        output_dir: Directory for output files

    Returns:
        Analysis response dict
    """
    orchestrator = CombosOrchestrator(output_dir)
    return orchestrator.analyze(
        rfc_file=rfc_file,
        qxdm_file=qxdm_file,
        uecap_file=uecap_file,
    )
