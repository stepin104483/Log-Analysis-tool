"""
Future Purpose Module

Placeholder for future analysis capabilities.
Status: Coming Soon
"""

import sys
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from core.placeholder_analyzer import PlaceholderAnalyzer


class FutureAnalyzer(PlaceholderAnalyzer):
    """Future Purpose Module - Placeholder"""

    @property
    def module_id(self) -> str:
        return "future"

    @property
    def display_name(self) -> str:
        return "Future Purpose"

    @property
    def description(self) -> str:
        return "Reserved for future analysis capabilities"

    @property
    def icon(self) -> str:
        return "lightbulb"
