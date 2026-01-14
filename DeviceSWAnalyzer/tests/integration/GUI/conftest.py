"""
Pytest fixtures for GUI module integration tests.
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
def sample_rfc_xml():
    """Sample RFC XML file content."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <band_name>B1</band_name>
    <band_name>B3</band_name>
    <band_name>N78</band_name>
</rfc_data>
'''


@pytest.fixture
def temp_upload_dir(tmp_path, app):
    """Create temporary upload directory."""
    upload_dir = tmp_path / "uploads" / "input"
    upload_dir.mkdir(parents=True)

    app.config['UPLOAD_FOLDER'] = str(upload_dir)

    return upload_dir


@pytest.fixture
def temp_output_dir(tmp_path, app):
    """Create temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)

    app.config['OUTPUT_FOLDER'] = str(output_dir)

    return output_dir
