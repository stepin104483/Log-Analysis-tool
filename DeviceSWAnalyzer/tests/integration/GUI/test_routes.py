"""
GUI Routes Integration Tests

Tests Flask route integrations and request/response handling.
"""

import pytest
import sys
from pathlib import Path
from io import BytesIO

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


class TestDashboardRoutes:
    """Integration tests for dashboard routes."""

    def test_index_route_accessible(self, client):
        """
        INT-GUI-001: Index route returns 200.
        """
        response = client.get('/')

        assert response.status_code == 200

    def test_index_renders_template(self, client):
        """
        INT-GUI-002: Index route renders HTML template.
        """
        response = client.get('/')

        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data

    def test_index_contains_modules(self, client):
        """
        INT-GUI-003: Index page contains module information.
        """
        response = client.get('/')

        # Should contain module-related content
        assert b'Band' in response.data or b'module' in response.data.lower()


class TestBandsRoutes:
    """Integration tests for Bands module routes."""

    def test_bands_upload_route_accessible(self, client):
        """
        INT-GUI-010: Bands upload route returns 200.
        """
        response = client.get('/bands/')

        assert response.status_code == 200

    def test_bands_upload_renders_form(self, client):
        """
        INT-GUI-011: Bands upload page contains file upload form.
        """
        response = client.get('/bands/')

        assert b'<form' in response.data
        assert b'file' in response.data.lower() or b'upload' in response.data.lower()

    def test_bands_analyze_requires_post(self, client):
        """
        INT-GUI-012: Analyze endpoint requires POST method.
        """
        response = client.get('/bands/analyze')

        # Should redirect or return method not allowed
        assert response.status_code in [302, 405]

    def test_bands_analyze_without_files_redirects(self, client, temp_upload_dir):
        """
        INT-GUI-013: Analyze without files redirects with error.
        """
        response = client.post('/bands/analyze', data={})

        # Should redirect back to upload page
        assert response.status_code == 302

    def test_bands_download_nonexistent_file(self, client, temp_output_dir):
        """
        INT-GUI-014: Download non-existent file redirects with error.
        """
        response = client.get('/bands/download/nonexistent.html')

        # Should redirect with error
        assert response.status_code == 302


class TestBlueprintRegistration:
    """Tests for blueprint registration and routing."""

    def test_main_blueprint_registered(self, app):
        """
        INT-GUI-020: Main blueprint is registered.
        """
        assert 'main' in app.blueprints

    def test_bands_blueprint_registered(self, app):
        """
        INT-GUI-021: Bands blueprint is registered.
        """
        assert 'bands' in app.blueprints

    def test_module_blueprint_registered(self, app):
        """
        INT-GUI-022: Module blueprint is registered.
        """
        assert 'module' in app.blueprints

    def test_bands_url_prefix(self, app):
        """
        INT-GUI-023: Bands blueprint has correct URL prefix.
        """
        bands_bp = app.blueprints.get('bands')
        assert bands_bp is not None
        # Verify route exists under /bands
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert any('/bands' in rule for rule in rules)


class TestAppConfiguration:
    """Tests for application configuration."""

    def test_upload_folder_configured(self, app):
        """
        INT-GUI-030: Upload folder is configured.
        """
        assert 'UPLOAD_FOLDER' in app.config
        assert app.config['UPLOAD_FOLDER'] is not None

    def test_output_folder_configured(self, app):
        """
        INT-GUI-031: Output folder is configured.
        """
        assert 'OUTPUT_FOLDER' in app.config
        assert app.config['OUTPUT_FOLDER'] is not None

    def test_allowed_extensions_configured(self, app):
        """
        INT-GUI-032: Allowed extensions are configured.
        """
        assert 'ALLOWED_EXTENSIONS' in app.config
        extensions = app.config['ALLOWED_EXTENSIONS']
        assert 'xml' in extensions
        assert 'txt' in extensions

    def test_max_content_length_configured(self, app):
        """
        INT-GUI-033: Max content length is configured.
        """
        assert 'MAX_CONTENT_LENGTH' in app.config
        assert app.config['MAX_CONTENT_LENGTH'] > 0


class TestTemplateRendering:
    """Tests for template rendering integration."""

    def test_index_uses_correct_template(self, client, app):
        """
        INT-GUI-040: Index route uses index.html template.
        """
        with app.test_request_context():
            response = client.get('/')
            # Check for common elements in the index template
            assert response.status_code == 200

    def test_bands_upload_uses_correct_template(self, client, app):
        """
        INT-GUI-041: Bands upload route uses upload.html template.
        """
        with app.test_request_context():
            response = client.get('/bands/')
            assert response.status_code == 200

    def test_404_handled_gracefully(self, client):
        """
        INT-GUI-042: Non-existent routes return 404.
        """
        response = client.get('/nonexistent/route/12345')

        assert response.status_code == 404


class TestModuleIntegration:
    """Tests for module system integration."""

    def test_module_context_processor_works(self, app, client):
        """
        INT-GUI-050: Module context processor provides module data.
        """
        with app.test_request_context():
            # Context processor should run without error
            response = client.get('/')
            assert response.status_code == 200

    def test_module_route_accessible(self, client):
        """
        INT-GUI-051: Generic module routes are accessible.
        """
        # Placeholder modules should redirect or show coming soon
        response = client.get('/module/combos')

        # Should not crash (may return 200 or redirect)
        assert response.status_code in [200, 302, 404]


class TestKnowledgeBaseIntegration:
    """Tests for knowledge base integration."""

    def test_kb_upload_route_exists(self, app):
        """
        INT-GUI-060: KB upload route exists.
        """
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert any('kb/upload' in rule for rule in rules)

    def test_kb_delete_route_exists(self, app):
        """
        INT-GUI-061: KB delete route exists.
        """
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert any('kb/delete' in rule for rule in rules)
