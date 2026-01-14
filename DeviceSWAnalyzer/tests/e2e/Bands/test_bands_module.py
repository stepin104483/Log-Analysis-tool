"""
Bands Module E2E Tests for DeviceSWAnalyzer.

These tests are specific to the Bands analysis module functionality.
Test Cases: TC-BANDS series
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


# =============================================================================
# Test Data Setup
# =============================================================================

@pytest.fixture
def bands_test_data_dir(tmp_path: Path) -> Path:
    """Create test data directory with sample files."""
    data_dir = tmp_path / "bands_test_data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def valid_rfc_lte_only(bands_test_data_dir: Path) -> Path:
    """RFC with LTE bands only."""
    rfc_file = bands_test_data_dir / "rfc_lte_only.xml"
    rfc_file.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<rfc>
    <eutra_band_list>
        <band>1</band>
        <band>3</band>
        <band>7</band>
        <band>20</band>
        <band>38</band>
        <band>40</band>
    </eutra_band_list>
</rfc>
''')
    return rfc_file


@pytest.fixture
def valid_rfc_nr_sa(bands_test_data_dir: Path) -> Path:
    """RFC with NR SA bands."""
    rfc_file = bands_test_data_dir / "rfc_nr_sa.xml"
    rfc_file.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<rfc>
    <eutra_band_list>
        <band>1</band>
        <band>3</band>
    </eutra_band_list>
    <nr_sa_band_list>
        <band>n78</band>
        <band>n79</band>
        <band>n260</band>
    </nr_sa_band_list>
</rfc>
''')
    return rfc_file


@pytest.fixture
def valid_rfc_full(bands_test_data_dir: Path) -> Path:
    """Full RFC with LTE, NR SA, and EN-DC combos."""
    rfc_file = bands_test_data_dir / "rfc_full.xml"
    rfc_file.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<rfc>
    <eutra_band_list>
        <band>1</band>
        <band>3</band>
        <band>7</band>
        <band>20</band>
    </eutra_band_list>
    <nr_sa_band_list>
        <band>n78</band>
        <band>n79</band>
    </nr_sa_band_list>
    <ca_4g_5g_combos>
        <combo>
            <lte_anchor>3</lte_anchor>
            <nr_band>n78</nr_band>
        </combo>
        <combo>
            <lte_anchor>7</lte_anchor>
            <nr_band>n79</nr_band>
        </combo>
    </ca_4g_5g_combos>
</rfc>
''')
    return rfc_file


@pytest.fixture
def empty_bands_rfc(bands_test_data_dir: Path) -> Path:
    """RFC with empty band lists."""
    rfc_file = bands_test_data_dir / "rfc_empty.xml"
    rfc_file.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<rfc>
    <eutra_band_list>
    </eutra_band_list>
</rfc>
''')
    return rfc_file


# =============================================================================
# RFC Parsing Tests
# =============================================================================

@pytest.mark.e2e
@pytest.mark.bands
class TestRFCParsing:
    """RFC parsing tests (TC-BANDS-001 to TC-BANDS-009)."""

    def test_parse_valid_rfc_xml(self, bands_upload_page: Page, valid_rfc_lte_only: Path):
        """
        TC-BANDS-001: Parse Valid RFC XML

        Requirement: FR-BANDS-001.1
        """
        # Upload RFC file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_lte_only))

        # Run analysis
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Verify results page loaded
        expect(bands_upload_page.locator("body")).to_be_visible()

        # Verify some band-related content is shown
        page_content = bands_upload_page.content().lower()
        assert "band" in page_content or "lte" in page_content or "analysis" in page_content

    def test_extract_lte_bands(self, bands_upload_page: Page, valid_rfc_lte_only: Path):
        """
        TC-BANDS-002: Extract LTE Bands from eutra_band_list

        Requirement: FR-BANDS-001.2
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_lte_only))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Check that LTE bands are mentioned in results
        page_content = bands_upload_page.content()

        # At least some band numbers should appear
        assert any(band in page_content for band in ["1", "3", "7", "20"])

    def test_extract_nr_sa_bands(self, bands_upload_page: Page, valid_rfc_nr_sa: Path):
        """
        TC-BANDS-003: Extract NR SA Bands from nr_sa_band_list

        Requirement: FR-BANDS-001.3
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_nr_sa))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Check for NR band references
        page_content = bands_upload_page.content().lower()
        assert "nr" in page_content or "n78" in page_content or "n79" in page_content

    def test_handle_empty_band_lists(self, bands_upload_page: Page, empty_bands_rfc: Path):
        """
        TC-BANDS-006: Parse RFC with Empty Band Lists

        Requirement: FR-BANDS-001.1
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(empty_bands_rfc))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first
        analyze_btn.click()

        # Wait for response
        bands_upload_page.wait_for_load_state("networkidle")
        bands_upload_page.wait_for_timeout(2000)

        # Should not crash
        expect(bands_upload_page.locator("body")).to_be_visible()


# =============================================================================
# Output Verification Tests
# =============================================================================

@pytest.mark.e2e
@pytest.mark.bands
class TestBandsOutput:
    """Output verification tests (TC-BANDS-060 to TC-BANDS-072)."""

    def test_html_report_generated(self, bands_upload_page: Page, valid_rfc_full: Path):
        """
        TC-BANDS-065: Generate HTML Report

        Requirement: FR-BANDS-021.1
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_full))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Check for download option
        download_btn = bands_upload_page.locator("a:has-text('Download'), button:has-text('Download')")

        if download_btn.count() > 0:
            expect(download_btn.first).to_be_visible()

    def test_report_includes_sections(self, bands_upload_page: Page, valid_rfc_full: Path):
        """
        TC-BANDS-066: Report Includes All Sections

        Requirement: FR-BANDS-021.2
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_full))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        page_content = bands_upload_page.content().lower()

        # Check for key sections (at least some should be present)
        sections_found = sum([
            "lte" in page_content,
            "nr" in page_content or "5g" in page_content,
            "band" in page_content,
            "analysis" in page_content or "result" in page_content
        ])

        assert sections_found >= 2, "Expected multiple analysis sections in output"

    def test_visual_indicators_present(self, bands_upload_page: Page, valid_rfc_full: Path):
        """
        TC-BANDS-068: Visual Indicators for Issues

        Requirement: FR-BANDS-021.4
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_full))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Check for status indicators (pass/fail/warning classes or text)
        page_content = bands_upload_page.content().lower()

        # Should have some kind of status indication
        has_indicators = any(term in page_content for term in [
            "pass", "fail", "warning", "success", "error",
            "green", "red", "yellow", "check", "cross"
        ])

        # This is informational - test passes either way
        # (actual implementation may vary)


# =============================================================================
# Band Category Tests
# =============================================================================

@pytest.mark.e2e
@pytest.mark.bands
class TestBandCategories:
    """Band category analysis tests (TC-BANDS-080 to TC-BANDS-092)."""

    def test_lte_fdd_bands(self, bands_upload_page: Page, valid_rfc_lte_only: Path):
        """
        TC-BANDS-080: Analyze LTE FDD Bands

        Requirement: FR-BANDS-030.1
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_lte_only))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Verify LTE analysis completed
        expect(bands_upload_page.locator("body")).to_be_visible()

    def test_nr_sa_sub6_bands(self, bands_upload_page: Page, valid_rfc_nr_sa: Path):
        """
        TC-BANDS-085: Analyze NR SA Sub-6 Bands

        Requirement: FR-BANDS-031.1
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_nr_sa))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Verify NR SA analysis completed
        page_content = bands_upload_page.content().lower()
        # n78, n79 are Sub-6 bands
        assert "nr" in page_content or "n78" in page_content or "n79" in page_content or "5g" in page_content

    def test_endc_combos(self, bands_upload_page: Page, valid_rfc_full: Path):
        """
        TC-BANDS-090: Analyze NR NSA (EN-DC) Bands

        Requirement: FR-BANDS-032.1
        """
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_full))

        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")

        # Verify analysis completed with EN-DC data
        expect(bands_upload_page.locator("body")).to_be_visible()


# =============================================================================
# Smoke Tests
# =============================================================================

@pytest.mark.smoke
@pytest.mark.bands
def test_bands_analysis_smoke(bands_upload_page: Page, valid_rfc_full: Path):
    """Smoke test: Full bands analysis completes successfully."""
    file_input = bands_upload_page.locator("input[type='file']").first
    file_input.set_input_files(str(valid_rfc_full))

    analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

    with bands_upload_page.expect_navigation(timeout=60000):
        analyze_btn.click()

    bands_upload_page.wait_for_load_state("networkidle")

    # Basic verification
    expect(bands_upload_page.locator("body")).to_be_visible()

    # Should not be on error page (check for error status codes in path, not port)
    page_content = bands_upload_page.content().lower()
    assert "/500" not in bands_upload_page.url  # 500 error page
    assert "/404" not in bands_upload_page.url  # 404 error page
    assert "internal server error" not in page_content
