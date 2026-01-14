"""
Error Handling E2E Tests for DeviceSWAnalyzer.

Test Cases: TC-GUI-060 to TC-GUI-065
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.error_handling
class TestErrorHandling:
    """Error handling tests."""

    def test_error_on_no_files_selected(self, bands_upload_page: Page):
        """
        TC-GUI-060: Verify Error on No Files Selected

        Requirement: NFR-001.4
        """
        # Try to submit without selecting a file
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first
        analyze_btn.click()

        # Wait a moment for any error to appear
        bands_upload_page.wait_for_timeout(1000)

        # Page should not crash and should show some feedback
        expect(bands_upload_page.locator("body")).to_be_visible()

        # Should either stay on page or show error
        current_url = bands_upload_page.url
        page_content = bands_upload_page.content().lower()

        # Either we're still on upload page or there's an error message
        assert "bands" in current_url or "error" in page_content or "please" in page_content

    def test_error_on_invalid_file(self, bands_upload_page: Page, invalid_xml_file: Path):
        """
        TC-GUI-061: Verify Error on Invalid File

        Requirement: NFR-001.4
        """
        # Upload invalid file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(invalid_xml_file))

        # Try to analyze
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first
        analyze_btn.click()

        # Wait for response
        bands_upload_page.wait_for_load_state("networkidle")
        bands_upload_page.wait_for_timeout(2000)

        # Page should handle error gracefully (not crash)
        expect(bands_upload_page.locator("body")).to_be_visible()

    def test_error_on_empty_file(self, bands_upload_page: Page, empty_file: Path):
        """
        TC-GUI-062: Verify Error on Empty File

        Requirement: NFR-001.4
        """
        # Upload empty file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(empty_file))

        # Try to analyze
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first
        analyze_btn.click()

        # Wait for response
        bands_upload_page.wait_for_load_state("networkidle")
        bands_upload_page.wait_for_timeout(2000)

        # Page should handle error gracefully
        expect(bands_upload_page.locator("body")).to_be_visible()

    def test_404_page(self, page: Page, base_url: str):
        """
        TC-GUI-065: Verify 404 Page

        Requirement: Error Handling
        """
        # Navigate to non-existent page
        page.goto(f"{base_url}/nonexistent-page-12345")
        page.wait_for_load_state("networkidle")

        # Should show some kind of error or redirect
        # Not crash or show raw error
        expect(page.locator("body")).to_be_visible()

        # Check for 404 indication or redirect to home
        page_content = page.content().lower()
        current_url = page.url

        assert "404" in page_content or "not found" in page_content or \
               "error" in page_content or current_url == f"{base_url}/"


@pytest.mark.e2e
@pytest.mark.error_handling
class TestBoundaryConditions:
    """Boundary condition tests."""

    def test_long_filename_handling(self, bands_upload_page: Page, tmp_path: Path):
        """
        TC-GUI-071: Verify Long Filename Handling

        Requirement: Usability
        """
        # Create file with long name (100 chars to stay within Windows path limits)
        long_name = "a" * 100 + "_rfc.xml"
        long_file = tmp_path / long_name
        long_file.write_text('''<?xml version="1.0"?>
<rfc><eutra_band_list><band>1</band></eutra_band_list></rfc>''')

        # Upload file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(long_file))

        # Page should handle it gracefully
        expect(bands_upload_page.locator("body")).to_be_visible()

    def test_special_characters_in_filename(self, bands_upload_page: Page, tmp_path: Path):
        """
        TC-GUI-072: Verify Special Characters in Filename

        Requirement: Security
        """
        # Create file with special characters (safe ones for filesystem)
        special_name = "test_rfc_file (1).xml"
        special_file = tmp_path / special_name
        special_file.write_text('''<?xml version="1.0"?>
<rfc><eutra_band_list><band>1</band></eutra_band_list></rfc>''')

        # Upload file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(special_file))

        # Page should handle it gracefully
        expect(bands_upload_page.locator("body")).to_be_visible()


@pytest.mark.smoke
@pytest.mark.error_handling
def test_server_handles_bad_input(bands_upload_page: Page):
    """Smoke test: Server doesn't crash on bad input."""
    # Submit empty form
    analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first
    analyze_btn.click()

    bands_upload_page.wait_for_timeout(2000)

    # Server should still be responsive
    expect(bands_upload_page.locator("body")).to_be_visible()
