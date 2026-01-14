"""
Pytest fixtures for DeviceSWAnalyzer E2E tests.

This module provides shared fixtures for Playwright-based E2E testing.
"""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect


# =============================================================================
# Configuration
# =============================================================================

BASE_URL = "http://localhost:5000"

# Test data paths
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "docs" / "testing" / "test_data"
VALID_DATA_DIR = TEST_DATA_DIR / "valid"
INVALID_DATA_DIR = TEST_DATA_DIR / "invalid"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
    return BASE_URL


@pytest.fixture
def home_page(page: Page, base_url: str) -> Page:
    """Navigate to home page and return page object."""
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture
def bands_upload_page(page: Page, base_url: str) -> Page:
    """Navigate to Bands upload page and return page object."""
    page.goto(f"{base_url}/bands")
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture
def module_page(page: Page, base_url: str):
    """Factory fixture to navigate to any module page."""
    def _navigate(module_id: str) -> Page:
        page.goto(f"{base_url}/module/{module_id}")
        page.wait_for_load_state("networkidle")
        return page
    return _navigate


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def valid_rfc_file():
    """Path to a valid RFC XML file for testing."""
    # Create a minimal valid RFC file if it doesn't exist
    rfc_path = VALID_DATA_DIR / "sample_rfc.xml"
    if not rfc_path.exists():
        VALID_DATA_DIR.mkdir(parents=True, exist_ok=True)
        rfc_path.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<rfc>
    <eutra_band_list>
        <band>1</band>
        <band>3</band>
        <band>7</band>
    </eutra_band_list>
    <nr_sa_band_list>
        <band>n78</band>
        <band>n79</band>
    </nr_sa_band_list>
</rfc>
''')
    return rfc_path


@pytest.fixture
def invalid_xml_file():
    """Path to an invalid XML file for negative testing."""
    invalid_path = INVALID_DATA_DIR / "malformed.xml"
    if not invalid_path.exists():
        INVALID_DATA_DIR.mkdir(parents=True, exist_ok=True)
        invalid_path.write_text('''<?xml version="1.0"?>
<rfc>
    <unclosed_tag>
    <band>1</band>
</rfc>
''')
    return invalid_path


@pytest.fixture
def empty_file():
    """Path to an empty file for boundary testing."""
    empty_path = INVALID_DATA_DIR / "empty.xml"
    if not empty_path.exists():
        INVALID_DATA_DIR.mkdir(parents=True, exist_ok=True)
        empty_path.write_text('')
    return empty_path


# =============================================================================
# Helper Fixtures
# =============================================================================

@pytest.fixture
def screenshot_on_failure(page: Page, request):
    """Take screenshot on test failure."""
    yield
    if request.node.rep_call.failed:
        screenshot_dir = Path(__file__).parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        page.screenshot(path=screenshot_dir / f"{request.node.name}.png")


# =============================================================================
# Custom Assertions
# =============================================================================

class PageAssertions:
    """Custom assertion helpers for page testing."""

    def __init__(self, page: Page):
        self.page = page

    def has_title(self, expected: str):
        """Assert page title contains expected text."""
        expect(self.page).to_have_title(expected)

    def has_url(self, expected: str):
        """Assert page URL matches expected."""
        expect(self.page).to_have_url(expected)

    def element_visible(self, selector: str):
        """Assert element is visible."""
        expect(self.page.locator(selector)).to_be_visible()

    def element_has_text(self, selector: str, text: str):
        """Assert element contains text."""
        expect(self.page.locator(selector)).to_contain_text(text)


@pytest.fixture
def assertions(page: Page) -> PageAssertions:
    """Page assertion helpers."""
    return PageAssertions(page)
