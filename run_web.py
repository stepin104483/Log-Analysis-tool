#!/usr/bin/env python
"""
Analysis Tool Web UI - Entry Point

Run this script to start the web interface:
    python run_web.py

Then open http://localhost:5000 in your browser.
"""
import os
import sys

# Prevent Python from writing .pyc cache files
sys.dont_write_bytecode = True

# Add paths in correct order:
# 1. DeviceSWAnalyzer (for modules.* imports)
# 2. DeviceSWAnalyzer/src (for web.* and core.* imports)
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.join(script_dir, 'DeviceSWAnalyzer')
src_dir = os.path.join(base_dir, 'src')

# Add base_dir FIRST so modules.combos finds DeviceSWAnalyzer/modules/
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
if src_dir not in sys.path:
    sys.path.insert(1, src_dir)

# Clear module registry cache to ensure fresh module discovery
from core import ModuleRegistry
ModuleRegistry.clear()

from web.app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  Analysis Tool Web UI")
    print("=" * 60)
    print()
    print("  Starting server...")
    print("  Open http://localhost:5000 in your browser")
    print()
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Run without debug to avoid caching issues
    app.run(debug=False, host='0.0.0.0', port=5000)
