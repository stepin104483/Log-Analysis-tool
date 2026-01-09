"""
Main Dashboard Routes
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render main dashboard with module tiles."""
    modules = [
        {
            'name': 'Bands',
            'description': 'Band filtering analysis',
            'url': '/bands',
            'active': True
        },
        {
            'name': 'Combos',
            'subtitle': '(CA, ENDC)',
            'description': 'Carrier Aggregation analysis',
            'url': '/coming-soon/combos',
            'active': False
        },
        {
            'name': 'IMS Support',
            'description': 'IMS capability analysis',
            'url': '/coming-soon/ims',
            'active': False
        },
        {
            'name': 'Supplementary Services',
            'description': 'SS feature analysis',
            'url': '/coming-soon/ss',
            'active': False
        },
        {
            'name': 'PICS',
            'description': 'Protocol Implementation Conformance',
            'url': '/coming-soon/pics',
            'active': False
        },
        {
            'name': 'Future Purpose',
            'description': 'Reserved for future modules',
            'url': '/coming-soon/future',
            'active': False
        }
    ]
    return render_template('index.html', modules=modules)


@main_bp.route('/coming-soon/<module_name>')
def coming_soon(module_name):
    """Render coming soon page for inactive modules."""
    return render_template('coming_soon.html', module_name=module_name)
