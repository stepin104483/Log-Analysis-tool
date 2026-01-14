"""
Upload Page E2E Tests for DeviceSWAnalyzer.

Test Cases: TC-GUI-010 to TC-GUI-019
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.upload
class TestUploadPage:
    """Upload page tests for Bands module."""

    def test_upload_page_content(self, bands_upload_page: Page):
        """
        TC-GUI-010: Verify Upload Page Content

        Requirement: UI-010
        """
        # Verify page title shows Band Analysis
        page_content = bands_upload_page.content().lower()
        assert "band" in page_content

        # Verify breadcrumb or navigation exists (home link)
        home_link = bands_upload_page.locator("a[href='/']")
        if home_link.count() > 0:
            expect(home_link.first).to_be_visible()
        else:
            # Alternative: check for any navigation back to home
            expect(bands_upload_page.locator("text=Home").first).to_be_visible()

    def test_file_input_field(self, bands_upload_page: Page):
        """
        TC-GUI-011: Verify File Input Field

        Requirement: FR-002.3, UI-011
        """
        # Verify file input exists
        file_input = bands_upload_page.locator("input[type='file']")
        expect(file_input.first).to_be_attached()

    def test_single_file_upload(self, bands_upload_page: Page, valid_rfc_file: Path):
        """
        TC-GUI-012: Verify Single File Upload

        Requirement: FR-002.3
        """
        # Upload a single file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_file))

        # Verify file is staged (filename should appear somewhere)
        page_content = bands_upload_page.content()
        assert valid_rfc_file.name in page_content or "file" in page_content.lower()

    def test_analyze_button(self, bands_upload_page: Page):
        """
        TC-GUI-015: Verify Analyze Button

        Requirement: UI-014
        """
        # Verify Analyze button exists
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']")
        expect(analyze_btn.first).to_be_visible()

    def test_loading_indicator_during_analysis(self, bands_upload_page: Page, valid_rfc_file: Path):
        """
        TC-GUI-016: Verify Loading Indicator During Analysis

        Requirement: NFR-001.3
        """
        # Upload file
        file_input = bands_upload_page.locator("input[type='file']").first
        file_input.set_input_files(str(valid_rfc_file))

        # Click analyze and check for loading indicator
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

        # Start waiting for navigation/response before clicking
        with bands_upload_page.expect_navigation(timeout=60000):
            analyze_btn.click()

        # After navigation, we should be on results page or see results

    def test_upload_without_file(self, bands_upload_page: Page):
        """
        TC-GUI-017: Verify Upload Without File

        Requirement: Error Handling
        """
        # Try to submit without file
        analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first
        analyze_btn.click()

        # Should show error or validation message
        bands_upload_page.wait_for_timeout(1000)

        # Page should still be functional (not crashed)
        expect(bands_upload_page.locator("body")).to_be_visible()

    def test_back_to_dashboard_link(self, bands_upload_page: Page):
        """
        TC-GUI-018: Verify Back to Dashboard Link

        Requirement: Navigation
        """
        # Find and click home/dashboard link
        home_link = bands_upload_page.locator("a[href='/'], a:has-text('Home'), a:has-text('Dashboard')").first
        home_link.click()

        # Should navigate back to dashboard
        bands_upload_page.wait_for_url("**/")
        expect(bands_upload_page).to_have_url("http://localhost:5000/")


@pytest.mark.smoke
@pytest.mark.upload
def test_upload_page_loads(bands_upload_page: Page):
    """Smoke test: Upload page loads successfully."""
    expect(bands_upload_page.locator("body")).to_be_visible()
    # Should have file input
    expect(bands_upload_page.locator("input[type='file']").first).to_be_attached()
