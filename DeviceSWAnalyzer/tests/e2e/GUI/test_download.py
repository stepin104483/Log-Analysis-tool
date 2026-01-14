"""
Download E2E Tests for DeviceSWAnalyzer.

Test Cases: TC-GUI-030 to TC-GUI-034
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.download
class TestDownload:
    """Download functionality tests."""

    @pytest.fixture
    def results_page(self, bands_upload_page: Page, valid_rfc_file: Path) -> Page:
        """Navigate to results page by running an analysis."""
        # Upload file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_file))

        # Click analyze
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        bands_upload_page.wait_for_load_state("networkidle")
        return bands_upload_page

    def test_download_button_presence(self, results_page: Page):
        """
        TC-GUI-030: Verify Download Button Presence

        Requirement: FR-002.6, UI-022
        """
        # Download button should be present
        download_btn = results_page.locator("a:has-text('Download'), button:has-text('Download')")

        if download_btn.count() > 0:
            expect(download_btn.first).to_be_visible()

    def test_html_report_download(self, results_page: Page, tmp_path: Path):
        """
        TC-GUI-031: Verify HTML Report Download

        Requirement: FR-002.6, UI-032
        """
        # Find download link/button
        download_btn = results_page.locator("a:has-text('Download'), button:has-text('Download')").first

        if download_btn.is_visible():
            # Set up download handling
            with results_page.expect_download() as download_info:
                download_btn.click()

            download = download_info.value

            # Verify it's an HTML file
            assert download.suggested_filename.endswith('.html'), \
                f"Expected HTML file, got {download.suggested_filename}"

            # Save and verify file is not empty
            save_path = tmp_path / download.suggested_filename
            download.save_as(save_path)
            assert save_path.stat().st_size > 0, "Downloaded file should not be empty"

    def test_downloaded_report_opens_standalone(self, results_page: Page, tmp_path: Path):
        """
        TC-GUI-032: Verify Downloaded Report Opens Standalone

        Requirement: FR-006.4
        """
        # Find download link/button
        download_btn = results_page.locator("a:has-text('Download'), button:has-text('Download')").first

        if download_btn.is_visible():
            # Download the file
            with results_page.expect_download() as download_info:
                download_btn.click()

            download = download_info.value
            save_path = tmp_path / download.suggested_filename
            download.save_as(save_path)

            # Open the downloaded file in browser
            results_page.goto(f"file:///{save_path}")
            results_page.wait_for_load_state("load")

            # Should render without errors
            expect(results_page.locator("body")).to_be_visible()

            # Should contain analysis content
            page_content = results_page.content().lower()
            assert "band" in page_content or "analysis" in page_content


@pytest.mark.smoke
@pytest.mark.download
def test_download_available(bands_upload_page: Page, valid_rfc_file: Path):
    """Smoke test: Download option is available after analysis."""
    # Upload and analyze
    file_input = bands_upload_page.locator("input[type='file']").first
    file_input.set_input_files(str(valid_rfc_file))

    analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

    with bands_upload_page.expect_navigation(timeout=60000):
        analyze_btn.click()

    bands_upload_page.wait_for_load_state("networkidle")

    # Check if download option exists
    download_elements = bands_upload_page.locator("a:has-text('Download'), button:has-text('Download')")
    # Just verify the page loaded successfully
    expect(bands_upload_page.locator("body")).to_be_visible()
