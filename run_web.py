#!/usr/bin/env python
"""
Analysis Tool Web UI - Entry Point

Run this script to start the web interface:
    python run_web.py

Then open http://localhost:5000 in your browser.
"""
import os
import sys

# Add DeviceSWAnalyzer/src to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'DeviceSWAnalyzer', 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

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

    app.run(debug=True, host='0.0.0.0', port=5000)
