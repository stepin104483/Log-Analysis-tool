"""
Band Explorer Module

Search and lookup tool for band information including BW, SCS, and combos.
Status: Coming Soon
"""

import sys
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from core.placeholder_analyzer import PlaceholderAnalyzer


class BandExplorerAnalyzer(PlaceholderAnalyzer):
    """
    Band Explorer Module

    A search/lookup tool for band information:
    - Supported Bandwidths
    - Subcarrier Spacing (SCS) for NR
    - Related CA combinations
    - EN-DC combinations
    - SA/NSA support details
    """

    @property
    def module_id(self) -> str:
        return "band_explorer"

    @property
    def display_name(self) -> str:
        return "Band Explorer"

    @property
    def description(self) -> str:
        return "Search band info: BW, SCS, CA/ENDC combos for SA & NSA"

    @property
    def icon(self) -> str:
        return "search"
