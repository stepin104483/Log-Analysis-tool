# E2E Testing with Playwright

This directory contains End-to-End (E2E) tests for DeviceSWAnalyzer using Playwright with Python.

## Prerequisites

- Python 3.8+
- Flask application running at `http://localhost:5000`

## Installation

### 1. Install test dependencies

```bash
cd DeviceSWAnalyzer
pip install -r requirements-test.txt
```

### 2. Install Playwright browsers

```bash
python -m playwright install
```

This will download Chromium, Firefox, and WebKit browsers.

## Running Tests

### Start the Flask application first

```bash
python run_web.py
```

### Run all E2E tests

```bash
python -m pytest tests/e2e/ -v
```

### Run module-specific tests

```bash
# Run GUI tests only
python -m pytest tests/e2e/GUI/ -v

# Run Bands module tests only
python -m pytest tests/e2e/Bands/ -v
```

### Run tests by marker

```bash
# Run only smoke tests
python -m pytest tests/e2e/ -m smoke

# Run only dashboard tests
python -m pytest tests/e2e/ -m dashboard

# Run only bands tests
python -m pytest tests/e2e/ -m bands

# Run only error handling tests
python -m pytest tests/e2e/ -m error_handling
```

### Run tests in different browsers

```bash
# Chromium (default)
python -m pytest tests/e2e/ --browser chromium

# Firefox
python -m pytest tests/e2e/ --browser firefox

# WebKit (Safari)
python -m pytest tests/e2e/ --browser webkit

# All browsers
python -m pytest tests/e2e/ --browser chromium --browser firefox --browser webkit
```

### Run tests headless (no browser window)

```bash
python -m pytest tests/e2e/ --headed=false
```

### Generate HTML report

```bash
python -m pytest tests/e2e/ -v --html=docs/testing/test_reports/e2e_report.html --self-contained-html
```

## Test Structure

```
tests/e2e/
├── __init__.py
├── conftest.py               # Shared fixtures and configuration
├── README.md                 # This file
│
├── GUI/                      # GUI Test Cases
│   ├── __init__.py
│   ├── test_dashboard.py     # TC-GUI-001 to TC-GUI-009
│   ├── test_upload.py        # TC-GUI-010 to TC-GUI-019
│   ├── test_results.py       # TC-GUI-020 to TC-GUI-029
│   ├── test_download.py      # TC-GUI-030 to TC-GUI-034
│   └── test_error_handling.py # TC-GUI-060 to TC-GUI-072
│
├── Bands/                    # Bands Module Test Cases
│   ├── __init__.py
│   └── test_bands_module.py  # TC-BANDS series
│
├── Combos/                   # Future: Combos Module Tests
├── IMS/                      # Future: IMS Module Tests
└── ...
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.e2e` | All E2E tests |
| `@pytest.mark.smoke` | Quick smoke tests |
| `@pytest.mark.dashboard` | Dashboard page tests |
| `@pytest.mark.upload` | Upload page tests |
| `@pytest.mark.results` | Results page tests |
| `@pytest.mark.download` | Download functionality tests |
| `@pytest.mark.error_handling` | Error handling tests |
| `@pytest.mark.bands` | Bands module tests |

## Configuration

### pytest.ini

The `pytest.ini` file in the project root contains default configuration:

- Default browser: Chromium
- Headed mode: Yes (shows browser)
- Slow motion: 100ms (for visibility)
- Base URL: http://localhost:5000

### Override settings

```bash
# Change base URL
python -m pytest tests/e2e/ --base-url http://localhost:8080

# Disable slow motion
python -m pytest tests/e2e/ --slowmo 0

# Increase timeout
python -m pytest tests/e2e/ --timeout 120
```

## Writing New Tests

### Basic test structure

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
@pytest.mark.your_marker
class TestYourFeature:
    """Your feature tests."""

    def test_something(self, home_page: Page):
        """
        TC-XXX-001: Test description

        Requirement: REQ-XXX
        """
        # Navigate
        home_page.click("text=Something")

        # Assert
        expect(home_page.locator(".result")).to_be_visible()
```

### Available fixtures

| Fixture | Description |
|---------|-------------|
| `page` | Fresh Playwright page (from pytest-playwright) |
| `base_url` | Base URL string |
| `home_page` | Page navigated to dashboard |
| `bands_upload_page` | Page navigated to Bands upload |
| `valid_rfc_file` | Path to valid test RFC file |
| `invalid_xml_file` | Path to invalid XML file |
| `empty_file` | Path to empty file |

## Troubleshooting

### Browser not found

```bash
python -m playwright install chromium
```

### Tests timeout

- Increase timeout: `python -m pytest --timeout 120`
- Check if Flask server is running
- Check if port 5000 is correct

### Tests fail in CI/CD

Run headless:
```bash
python -m pytest tests/e2e/ --headed=false
```

### Screenshots on failure

Screenshots are saved to `tests/e2e/screenshots/` on test failure.

## Mapping to Test Cases

### GUI Tests

| Test File | Test Cases |
|-----------|------------|
| GUI/test_dashboard.py | TC-GUI-001 to TC-GUI-009 |
| GUI/test_upload.py | TC-GUI-010 to TC-GUI-019 |
| GUI/test_results.py | TC-GUI-020 to TC-GUI-029 |
| GUI/test_download.py | TC-GUI-030 to TC-GUI-034 |
| GUI/test_error_handling.py | TC-GUI-060 to TC-GUI-072 |

### Bands Module Tests

| Test File | Test Cases |
|-----------|------------|
| Bands/test_bands_module.py | TC-BANDS series |
