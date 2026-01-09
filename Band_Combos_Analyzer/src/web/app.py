"""
Flask Application Factory for Analysis Tool Web UI
"""
import os
from flask import Flask


def create_app():
    """Create and configure the Flask application."""

    # Get the base directory (Band_Combos_Analyzer)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Get the root directory (Log-Analysis-tool)
    root_dir = os.path.dirname(base_dir)

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )

    # Configuration
    app.config['SECRET_KEY'] = 'analysis-tool-secret-key-change-in-production'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

    # Upload folders
    app.config['UPLOAD_FOLDER'] = os.path.join(root_dir, 'uploads', 'input')
    app.config['KNOWLEDGE_LIBRARY'] = os.path.join(root_dir, 'knowledge_library')
    app.config['OUTPUT_FOLDER'] = os.path.join(base_dir, 'output')

    # Allowed file extensions
    app.config['ALLOWED_EXTENSIONS'] = {'xml', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'bin', 'hex'}

    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['KNOWLEDGE_LIBRARY'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes.main import main_bp
    from .routes.bands import bands_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(bands_bp, url_prefix='/bands')

    return app


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
