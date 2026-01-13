"""
Flask Application Factory for Analysis Tool Web UI

Uses plugin-based architecture with auto-discovery of modules.
"""
import os
import sys
import logging
from flask import Flask

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""

    # Get the base directory (DeviceSWAnalyzer)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Get the root directory (Log-Analysis-tool)
    root_dir = os.path.dirname(base_dir)

    # Add base_dir to path for module imports
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

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
    app.config['BASE_DIR'] = base_dir

    # Allowed file extensions
    app.config['ALLOWED_EXTENSIONS'] = {'xml', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'bin', 'hex', 'json', 'csv'}

    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['KNOWLEDGE_LIBRARY'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # Discover and register modules
    modules_path = os.path.join(base_dir, 'modules')
    try:
        from core import ModuleRegistry
        ModuleRegistry.discover_modules(modules_path)
        logger.info(f"Modules discovered: {list(ModuleRegistry.get_all_modules().keys())}")
    except Exception as e:
        logger.error(f"Failed to discover modules: {e}")

    # Register blueprints
    from .routes.main import main_bp
    from .routes.bands import bands_bp
    from .routes.module import module_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(bands_bp, url_prefix='/bands')  # Keep legacy bands routes
    app.register_blueprint(module_bp, url_prefix='/module')  # New generic module routes

    # Make module registry available in templates
    @app.context_processor
    def inject_modules():
        try:
            from core import ModuleRegistry
            return {
                'all_modules': ModuleRegistry.get_module_list(),
                'active_modules': [m.get_module_info() for m in ModuleRegistry.get_active_modules().values()]
            }
        except:
            return {'all_modules': [], 'active_modules': []}

    return app


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
