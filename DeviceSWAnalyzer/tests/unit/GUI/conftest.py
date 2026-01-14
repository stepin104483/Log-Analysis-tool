"""
Pytest fixtures for GUI module unit tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


@pytest.fixture
def app():
    """Create Flask application for testing."""
    from src.web.app import create_app

    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield app


@pytest.fixture
def sample_html_report():
    """Sample HTML report for testing."""
    return '''<!DOCTYPE html>
<html>
<head><title>Test Report</title></head>
<body>
    <div class="section">
        <div class="section-header">
            <h2>Summary</h2>
        </div>
        <div class="section-content">
            <p>Test summary content</p>
        </div>
    </div>
</body>
</html>
'''


@pytest.fixture
def sample_claude_review():
    """Sample Claude review for testing."""
    return '''## 1. Analysis Overview

This is a test review.

## 2. Findings

- Finding 1
- Finding 2

## 3. Overall Verdict

**Safe to deploy** - All bands configured correctly.

## 4. Recommendations

1. Monitor band performance
2. Review carrier policy
'''


@pytest.fixture
def temp_kb_dir(tmp_path):
    """Create temporary knowledge base directory."""
    kb_dir = tmp_path / "knowledge_library"
    kb_dir.mkdir()

    # Create some test files
    (kb_dir / "test_doc.pdf").write_text("PDF content")
    (kb_dir / "test_data.xml").write_text("<data>test</data>")

    return kb_dir
