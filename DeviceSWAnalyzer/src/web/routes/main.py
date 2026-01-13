"""
Main Dashboard Routes

Dynamically renders dashboard with modules from the ModuleRegistry.
"""
import sys
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for

# Add path for imports
base_dir = Path(__file__).parent.parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

main_bp = Blueprint('main', __name__)


# Define module order for display
MODULE_ORDER = ['bands', 'combos', 'ims', 'supplementary_services', 'pics', 'band_explorer', 'future']


@main_bp.route('/')
def index():
    """Render main dashboard with module tiles from registry."""
    try:
        from core import ModuleRegistry

        # Get all registered modules
        all_modules = ModuleRegistry.get_all_modules()

        # Build modules list for template in specified order
        modules = []
        for module_id in MODULE_ORDER:
            if module_id in all_modules:
                module = all_modules[module_id]
                info = module.get_module_info()

                # Determine URL based on module status
                if info['status'] == 'active':
                    # Use legacy /bands route for bands, /module/<id> for others
                    if module_id == 'bands':
                        url = '/bands'
                    else:
                        url = f'/module/{module_id}'
                else:
                    url = f'/module/{module_id}'

                modules.append({
                    'name': info['display_name'],
                    'description': info['description'],
                    'url': url,
                    'active': info['status'] == 'active',
                    'module_id': module_id,
                    'icon': info.get('icon', 'default')
                })

        # If no modules discovered, fall back to default list
        if not modules:
            modules = _get_default_modules()

    except Exception as e:
        print(f"[ERROR] Failed to load modules from registry: {e}", flush=True)
        modules = _get_default_modules()

    return render_template('index.html', modules=modules)


def _get_default_modules():
    """Fallback module list if registry fails."""
    return [
        {
            'name': 'Bands',
            'description': 'Band filtering analysis',
            'url': '/bands',
            'active': True,
            'module_id': 'bands'
        },
        {
            'name': 'Combos (CA, ENDC)',
            'description': 'Carrier Aggregation analysis',
            'url': '/module/combos',
            'active': False,
            'module_id': 'combos'
        },
        {
            'name': 'IMS Support',
            'description': 'IMS capability analysis',
            'url': '/module/ims',
            'active': False,
            'module_id': 'ims'
        },
        {
            'name': 'Supp Services',
            'description': 'SS feature analysis',
            'url': '/module/supplementary_services',
            'active': False,
            'module_id': 'supplementary_services'
        },
        {
            'name': 'PICS',
            'description': 'Protocol Implementation Conformance',
            'url': '/module/pics',
            'active': False,
            'module_id': 'pics'
        },
        {
            'name': 'Band Explorer',
            'description': 'Search band info: BW, SCS, combos',
            'url': '/module/band_explorer',
            'active': False,
            'module_id': 'band_explorer'
        },
        {
            'name': 'Future Purpose',
            'description': 'Reserved for future modules',
            'url': '/module/future',
            'active': False,
            'module_id': 'future'
        }
    ]


@main_bp.route('/coming-soon/<module_name>')
def coming_soon(module_name):
    """Redirect to module page (handles legacy coming-soon URLs)."""
    return redirect(url_for('module.upload', module_id=module_name))
