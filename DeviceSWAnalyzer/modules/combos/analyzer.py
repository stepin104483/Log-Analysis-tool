"""
Combos Analysis Module (CA, EN-DC)

Analyzes carrier aggregation and EN-DC combinations.
Status: Coming Soon
"""

import sys
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from core.placeholder_analyzer import PlaceholderAnalyzer


class CombosAnalyzer(PlaceholderAnalyzer):
    """
    Combos (CA, EN-DC) Analysis Module

    Will analyze carrier aggregation combinations and EN-DC configurations.
    """

    @property
    def module_id(self) -> str:
        return "combos"

    @property
    def display_name(self) -> str:
        return "Combos (CA, ENDC)"

    @property
    def description(self) -> str:
        return "Analyze carrier aggregation and EN-DC combinations"

    @property
    def icon(self) -> str:
        return "layers"
