"""
Band Combos Analyzer - Output Package

This package contains output generators:
- ConsoleReport: Terminal/console output
- HTMLReport: Downloadable HTML report
"""

from .console_report import ConsoleReport, print_console_report, get_console_report
from .html_report import HTMLReport, generate_html_report

__all__ = [
    'ConsoleReport', 'print_console_report', 'get_console_report',
    'HTMLReport', 'generate_html_report',
]
