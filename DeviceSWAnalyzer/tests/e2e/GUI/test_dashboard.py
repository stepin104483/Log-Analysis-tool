"""
Dashboard E2E Tests for DeviceSWAnalyzer.

Test Cases: TC-GUI-001 to TC-GUI-009
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.dashboard
class TestDashboard:
    """Dashboard page tests."""

    def test_dashboard_displays_all_modules(self, home_page: Page):
        """
        TC-GUI-001: Verify Dashboard Displays All Modules

        Requirement: FR-002.1, UI-001
        """
        # Verify page loads
        expect(home_page).to_have_url("http://localhost:5000/")

        # Verify all 7 modules are displayed by checking their names
        module_names = ["Band Analysis", "Combos", "IMS", "Supp Services", "PICS", "Band Explorer", "Future"]
        for name in module_names:
            expect(home_page.locator(f"text={name}").first).to_be_visible()

    def test_module_tile_content(self, home_page: Page):
        """
        TC-GUI-002: Verify Module Tile Content

        Requirement: UI-005
        """
        # Check that module tiles have name and description
        # Bands module should be visible
        bands_tile = home_page.locator("text=Band Analysis").first
        expect(bands_tile).to_be_visible()

        # Combos module should be visible
        combos_tile = home_page.locator("text=Combos").first
        expect(combos_tile).to_be_visible()

    def test_active_module_visual_style(self, home_page: Page):
        """
        TC-GUI-003: Verify Active Module Visual Style

        Requirement: FR-002.2, UI-002
        """
        # Bands is the only active module - should not have "Coming Soon"
        bands_section = home_page.locator("text=Band Analysis").first
        expect(bands_section).to_be_visible()

        # Verify it's clickable (has link/button behavior)
        bands_link = home_page.locator("a:has-text('Band Analysis'), [href*='bands']").first
        expect(bands_link).to_be_visible()

    def test_coming_soon_module_visual_style(self, home_page: Page):
        """
        TC-GUI-004: Verify Coming Soon Module Visual Style

        Requirement: FR-002.2, UI-002
        """
        # Coming soon modules should have visual indicator
        # Check for "Coming Soon" text or badge near Combos, IMS, etc.
        page_content = home_page.content()

        # At least one "Coming Soon" indicator should exist
        coming_soon_elements = home_page.locator("text=/coming soon/i")
        expect(coming_soon_elements.first).to_be_visible()

    def test_active_module_navigation(self, home_page: Page):
        """
        TC-GUI-005: Verify Active Module Navigation

        Requirement: UI-003
        """
        # Click on Bands module
        home_page.click("a:has-text('Band'), [href*='bands']")

        # Should navigate to bands page
        home_page.wait_for_url("**/bands**")

        # Verify URL contains 'bands'
        assert "bands" in home_page.url

        # Verify we're on the upload page
        expect(home_page.locator("text=/upload|analyze/i").first).to_be_visible()

    def test_coming_soon_module_navigation(self, home_page: Page):
        """
        TC-GUI-006: Verify Coming Soon Module Navigation

        Requirement: UI-004
        """
        # Click on a coming soon module (e.g., Combos)
        home_page.click("a:has-text('Combos'), [href*='combos']")

        # Should show coming soon page or message
        home_page.wait_for_load_state("networkidle")

        # Verify coming soon message is displayed
        expect(home_page.locator("text=/coming soon/i").first).to_be_visible()

    def test_all_coming_soon_modules_show_placeholder(self, home_page: Page, base_url: str):
        """
        TC-GUI-007: Verify All Coming Soon Modules Show Placeholder

        Requirement: UI-004
        """
        coming_soon_modules = ['combos', 'ims', 'supplementary_services', 'pics', 'band_explorer', 'future']

        for module_id in coming_soon_modules:
            home_page.goto(f"{base_url}/module/{module_id}")
            home_page.wait_for_load_state("networkidle")

            # Each should show coming soon or placeholder
            page_text = home_page.content().lower()
            assert "coming soon" in page_text or "not available" in page_text or "placeholder" in page_text, \
                f"Module {module_id} should show placeholder page"

    def test_dashboard_header(self, home_page: Page):
        """
        TC-GUI-008: Verify Dashboard Header

        Requirement: UI Design
        """
        # Verify page has a header/title
        header = home_page.locator("h1, .header, .title, header").first
        expect(header).to_be_visible()

    def test_dashboard_responsive_layout(self, home_page: Page):
        """
        TC-GUI-009: Verify Dashboard Responsive Layout

        Requirement: Usability
        """
        # Test different viewport sizes
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1024, "height": 768},
        ]

        for viewport in viewports:
            home_page.set_viewport_size(viewport)
            home_page.wait_for_timeout(500)

            # Modules should still be visible
            modules = home_page.locator(".module-tile, .card, [class*='module']")
            expect(modules.first).to_be_visible()


@pytest.mark.smoke
@pytest.mark.dashboard
def test_dashboard_loads(home_page: Page):
    """Smoke test: Dashboard loads successfully."""
    expect(home_page).to_have_url("http://localhost:5000/")
    expect(home_page.locator("body")).to_be_visible()
