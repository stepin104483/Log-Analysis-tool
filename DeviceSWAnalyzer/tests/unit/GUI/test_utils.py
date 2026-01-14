"""
GUI Utility Functions Unit Tests

Tests individual utility functions used in the GUI.
"""

import pytest
import sys
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


class TestAllowedFile:
    """Tests for allowed_file function."""

    def test_allowed_xml_extension(self, app_context):
        """
        TC-GUI-UNIT-001: XML files are allowed.
        """
        from src.web.app import allowed_file

        assert allowed_file('test.xml', {'xml', 'txt'}) is True

    def test_allowed_txt_extension(self, app_context):
        """
        TC-GUI-UNIT-002: TXT files are allowed.
        """
        from src.web.app import allowed_file

        assert allowed_file('test.txt', {'xml', 'txt'}) is True

    def test_disallowed_extension(self, app_context):
        """
        TC-GUI-UNIT-003: EXE files are not allowed.
        """
        from src.web.app import allowed_file

        assert allowed_file('test.exe', {'xml', 'txt'}) is False

    def test_no_extension(self, app_context):
        """
        TC-GUI-UNIT-004: Files without extension are not allowed.
        """
        from src.web.app import allowed_file

        assert allowed_file('testfile', {'xml', 'txt'}) is False

    def test_case_insensitive(self, app_context):
        """
        TC-GUI-UNIT-005: Extension check is case insensitive.
        """
        from src.web.app import allowed_file

        assert allowed_file('test.XML', {'xml', 'txt'}) is True
        assert allowed_file('test.TXT', {'xml', 'txt'}) is True

    def test_double_extension(self, app_context):
        """
        TC-GUI-UNIT-006: Only last extension is checked.
        """
        from src.web.app import allowed_file

        assert allowed_file('test.tar.xml', {'xml', 'txt'}) is True
        assert allowed_file('test.xml.exe', {'xml', 'txt'}) is False


class TestDetectFileType:
    """Tests for detect_file_type function."""

    def test_detect_rfc_file(self, app_context):
        """
        TC-GUI-UNIT-010: RFC files are detected correctly.
        """
        from src.web.routes.bands import detect_file_type

        assert detect_file_type('rfc_data.xml') == 'rfc_path'
        assert detect_file_type('RFC_CARD.xml') == 'rfc_path'
        assert detect_file_type('my_rfc_file.xml') == 'rfc_path'

    def test_detect_hw_filter_file(self, app_context):
        """
        TC-GUI-UNIT-011: HW filter files are detected correctly.
        """
        from src.web.routes.bands import detect_file_type

        assert detect_file_type('hardware_band_filtering.xml') == 'hw_filter_path'
        assert detect_file_type('hw_filter.xml') == 'hw_filter_path'

    def test_detect_carrier_policy_file(self, app_context):
        """
        TC-GUI-UNIT-012: Carrier policy files are detected correctly.
        """
        from src.web.routes.bands import detect_file_type

        assert detect_file_type('carrier_policy.xml') == 'carrier_policy_path'
        assert detect_file_type('CARRIER_POLICY_VZW.xml') == 'carrier_policy_path'

    def test_detect_qxdm_log_file(self, app_context):
        """
        TC-GUI-UNIT-013: QXDM log files are detected correctly.
        """
        from src.web.routes.bands import detect_file_type

        assert detect_file_type('qxdm_log.txt') == 'qxdm_log_path'
        assert detect_file_type('pm_rf_bands.txt') == 'qxdm_log_path'
        assert detect_file_type('0x1cca_output.txt') == 'qxdm_log_path'

    def test_detect_ue_capability_file(self, app_context):
        """
        TC-GUI-UNIT-014: UE capability files are detected correctly.
        """
        from src.web.routes.bands import detect_file_type

        assert detect_file_type('ue_capability.txt') == 'ue_capability_path'
        assert detect_file_type('UE_CAP_INFO.txt') == 'ue_capability_path'

    def test_unknown_file_returns_none(self, app_context):
        """
        TC-GUI-UNIT-015: Unknown files return None.
        """
        from src.web.routes.bands import detect_file_type

        assert detect_file_type('random_file.xml') is None
        assert detect_file_type('data.txt') is None
        assert detect_file_type('image.png') is None


class TestGetDefaultModules:
    """Tests for _get_default_modules function."""

    def test_returns_list(self, app_context):
        """
        TC-GUI-UNIT-020: Returns a list of modules.
        """
        from src.web.routes.main import _get_default_modules

        modules = _get_default_modules()

        assert isinstance(modules, list)
        assert len(modules) > 0

    def test_module_structure(self, app_context):
        """
        TC-GUI-UNIT-021: Each module has required fields.
        """
        from src.web.routes.main import _get_default_modules

        modules = _get_default_modules()

        for module in modules:
            assert 'name' in module
            assert 'description' in module
            assert 'url' in module
            assert 'active' in module
            assert 'module_id' in module

    def test_bands_module_is_active(self, app_context):
        """
        TC-GUI-UNIT-022: Bands module is marked as active.
        """
        from src.web.routes.main import _get_default_modules

        modules = _get_default_modules()
        bands = next((m for m in modules if m['module_id'] == 'bands'), None)

        assert bands is not None
        assert bands['active'] is True

    def test_placeholder_modules_inactive(self, app_context):
        """
        TC-GUI-UNIT-023: Placeholder modules are marked as inactive.
        """
        from src.web.routes.main import _get_default_modules

        modules = _get_default_modules()
        placeholders = [m for m in modules if m['module_id'] != 'bands']

        for placeholder in placeholders:
            assert placeholder['active'] is False


class TestInjectClaudeReview:
    """Tests for inject_claude_review function."""

    def test_injects_claude_section(self, app_context, sample_html_report, sample_claude_review):
        """
        TC-GUI-UNIT-030: Injects Claude review section into HTML.
        """
        from src.web.routes.bands import inject_claude_review

        result = inject_claude_review(sample_html_report, sample_claude_review)

        assert 'Claude Expert Review' in result
        assert 'Stage 2' in result

    def test_preserves_original_content(self, app_context, sample_html_report, sample_claude_review):
        """
        TC-GUI-UNIT-031: Original HTML content is preserved.
        """
        from src.web.routes.bands import inject_claude_review

        result = inject_claude_review(sample_html_report, sample_claude_review)

        assert 'Test summary content' in result
        assert '<title>Test Report</title>' in result

    def test_adds_styles(self, app_context, sample_html_report, sample_claude_review):
        """
        TC-GUI-UNIT-032: CSS styles are added.
        """
        from src.web.routes.bands import inject_claude_review

        result = inject_claude_review(sample_html_report, sample_claude_review)

        assert '<style>' in result
        assert '.claude-review-section' in result

    def test_renders_markdown_tables(self, app_context, sample_html_report):
        """
        TC-GUI-UNIT-033: Markdown tables are rendered as HTML.
        """
        from src.web.routes.bands import inject_claude_review

        review_with_table = '''## Summary

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
'''
        result = inject_claude_review(sample_html_report, review_with_table)

        assert '<table>' in result or '<table ' in result

    def test_extracts_verdict_section(self, app_context, sample_html_report, sample_claude_review):
        """
        TC-GUI-UNIT-034: Verdict section is extracted and highlighted.
        """
        from src.web.routes.bands import inject_claude_review

        result = inject_claude_review(sample_html_report, sample_claude_review)

        assert 'verdict-section' in result or 'Verdict' in result

    def test_handles_unicode_characters(self, app_context, sample_html_report):
        """
        TC-GUI-UNIT-035: Unicode characters are handled correctly.
        """
        from src.web.routes.bands import inject_claude_review

        review_with_unicode = '''## Verdict

✓ All tests passed
✗ No errors found
'''
        result = inject_claude_review(sample_html_report, review_with_unicode)

        # Should not crash and should have content
        assert len(result) > len(sample_html_report)
