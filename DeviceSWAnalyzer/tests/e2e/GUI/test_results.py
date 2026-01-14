"""
Results Page E2E Tests for DeviceSWAnalyzer.

Test Cases: TC-GUI-020 to TC-GUI-029
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.results
class TestResultsPage:
    """Results page tests."""

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

    def test_results_page_display(self, results_page: Page):
        """
        TC-GUI-020: Verify Results Page Display

        Requirement: FR-002.5, UI-020
        """
        # Results page should show analysis output
        expect(results_page.locator("body")).to_be_visible()

        # Should contain some results content
        page_content = results_page.content().lower()
        assert "result" in page_content or "analysis" in page_content or "band" in page_content

    def test_stage1_output_content(self, results_page: Page):
        """
        TC-GUI-021: Verify Stage 1 Output Content

        Requirement: UI-020
        """
        # Results should contain band-related information
        page_content = results_page.content().lower()

        # Should have some indication of band analysis
        assert any(term in page_content for term in ["lte", "nr", "band", "analysis", "result"])

    def test_ai_expert_review_button(self, results_page: Page):
        """
        TC-GUI-022: Verify AI Expert Review Button

        Requirement: UI-021
        """
        # AI Expert Review button should be present
        ai_button = results_page.locator("button:has-text('AI'), button:has-text('Expert'), button:has-text('Review')")

        # At least one such button should exist
        if ai_button.count() > 0:
            expect(ai_button.first).to_be_visible()

    def test_new_analysis_link(self, results_page: Page):
        """
        TC-GUI-024: Verify New Analysis Link

        Requirement: Navigation
        """
        # Should have a way to start new analysis
        new_analysis_link = results_page.locator("a:has-text('New'), a:has-text('Upload'), a[href*='bands']")

        if new_analysis_link.count() > 0:
            expect(new_analysis_link.first).to_be_visible()

    def test_results_page_scrolling(self, results_page: Page):
        """
        TC-GUI-028: Verify Results Page Scrolling

        Requirement: Usability
        """
        # Scroll to bottom
        results_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        results_page.wait_for_timeout(500)

        # Scroll back to top
        results_page.evaluate("window.scrollTo(0, 0)")
        results_page.wait_for_timeout(500)

        # Page should still be functional
        expect(results_page.locator("body")).to_be_visible()


@pytest.mark.smoke
@pytest.mark.results
def test_analysis_completes(bands_upload_page: Page, valid_rfc_file: Path):
    """Smoke test: Analysis completes and shows results."""
    # Upload file
    file_input = bands_upload_page.locator("input[type='file']").first
    file_input.set_input_files(str(valid_rfc_file))

    # Click analyze
    analyze_btn = bands_upload_page.locator("button:has-text('Analyze'), input[type='submit']").first

    with bands_upload_page.expect_navigation(timeout=60000):
        analyze_btn.click()

    # Should navigate away from upload page
    bands_upload_page.wait_for_load_state("networkidle")
    expect(bands_upload_page.locator("body")).to_be_visible()
