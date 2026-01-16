"""
RFC (RF Card) XML Parser for Combos

Parses RFC XML files to extract CA/DC combo definitions.

RFC combo format examples:
    LTE CA:     B1A[4];A[1]+B3A[4];A[1]
    EN-DC:      B1A[4];A[1]+N77A[100x4];A[100x1]
    Multi-band: B66A[4];A[1]+B66A[4]+N77A[100x4];A[100x1]

Format breakdown:
    B66A[4];A[1] = Band 66, Class A, 4 DL layers, 1 UL layer
    N77A[100x4];A[100x1] = NR Band 77, Class A, 100MHz x 4 layers
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from ..models import (
    ComboType,
    DataSource,
    BandComponent,
    Combo,
    ComboSet,
)


class RFCParser:
    """Parse RFC XML files for combo definitions."""

    def __init__(self):
        self.file_info: Dict[str, str] = {}
        self._parse_errors: List[str] = []

    def parse(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse RFC XML and return combo sets by type.

        Args:
            file_path: Path to RFC XML file

        Returns:
            Dict mapping ComboType to ComboSet
        """
        self._parse_errors = []
        result = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RFC, combo_type=ComboType.LTE_CA),
            ComboType.ENDC: ComboSet(source=DataSource.RFC, combo_type=ComboType.ENDC),
            ComboType.NRCA: ComboSet(source=DataSource.RFC, combo_type=ComboType.NRCA),
            ComboType.NRDC: ComboSet(source=DataSource.RFC, combo_type=ComboType.NRDC),
        }

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            self._parse_errors.append(f"XML parse error: {e}")
            return result
        except FileNotFoundError:
            self._parse_errors.append(f"File not found: {file_path}")
            return result

        # Extract file info
        self._extract_file_info(root, file_path)

        # Parse LTE CA combos from ca_combos section
        lte_ca_combos = self._parse_lte_ca_combos(root)
        for combo in lte_ca_combos:
            result[ComboType.LTE_CA].add(combo)

        # Parse EN-DC combos from ca_4g_5g_combos section
        endc_combos = self._parse_endc_combos(root)
        for combo in endc_combos:
            result[ComboType.ENDC].add(combo)

        # Parse NR CA combos from nrca_combos section (if exists)
        nrca_combos = self._parse_nrca_combos(root)
        for combo in nrca_combos:
            result[ComboType.NRCA].add(combo)

        # Parse NR-DC combos (if exists)
        nrdc_combos = self._parse_nrdc_combos(root)
        for combo in nrdc_combos:
            result[ComboType.NRDC].add(combo)

        return result

    def _extract_file_info(self, root: ET.Element, file_path: str):
        """Extract file info from RFC XML."""
        self.file_info = {
            'file_path': file_path,
            'hwid': '',
            'name': '',
        }

        # Try to find card_properties
        card_props = root.find('.//card_properties')
        if card_props is not None:
            hwid_elem = card_props.find('hwid')
            name_elem = card_props.find('name')

            if hwid_elem is not None and hwid_elem.text:
                self.file_info['hwid'] = hwid_elem.text.strip()
            if name_elem is not None and name_elem.text:
                self.file_info['name'] = name_elem.text.strip()

    def _parse_lte_ca_combos(self, root: ET.Element) -> List[Combo]:
        """
        Parse LTE CA combos from <ca_combos> section.

        Format: B1A[4];A[1]+B3A[4];A[1]
        """
        combos = []

        # Find ca_combos section (pure LTE CA, no NR)
        for combos_elem in root.iter('ca_combos'):
            for combo_elem in combos_elem.iter('ca_combo'):
                if combo_elem.text:
                    combo_text = combo_elem.text.strip()
                    # Skip if it contains NR bands (those are EN-DC)
                    if 'N' in combo_text.upper() and re.search(r'N\d+', combo_text, re.IGNORECASE):
                        continue

                    combo = self._parse_combo_string(combo_text, ComboType.LTE_CA)
                    if combo and len(combo.components) > 0:
                        combos.append(combo)

        return combos

    def _parse_endc_combos(self, root: ET.Element) -> List[Combo]:
        """
        Parse EN-DC combos from <ca_4g_5g_combos> section.

        Format: B1A[4];A[1]+N77A[100x4];A[100x1]
        """
        combos = []

        # Find ca_4g_5g_combos section (EN-DC)
        for combos_elem in root.iter('ca_4g_5g_combos'):
            for combo_elem in combos_elem.iter('ca_combo'):
                if combo_elem.text:
                    combo_text = combo_elem.text.strip()
                    combo = self._parse_combo_string(combo_text, ComboType.ENDC)
                    if combo and len(combo.lte_components) > 0 and len(combo.nr_components) > 0:
                        combos.append(combo)

        return combos

    def _parse_nrca_combos(self, root: ET.Element) -> List[Combo]:
        """
        Parse NR CA combos from <nrca_combos> or similar section.

        Format: N77A[100x4];A[100x1]+N78A[100x4];A[100x1]
        """
        combos = []

        # Find nrca_combos section
        for combos_elem in root.iter('nrca_combos'):
            for combo_elem in combos_elem.iter('ca_combo'):
                if combo_elem.text:
                    combo_text = combo_elem.text.strip()
                    combo = self._parse_combo_string(combo_text, ComboType.NRCA)
                    if combo and len(combo.nr_components) > 0:
                        combos.append(combo)

        # Also check nr_ca_combos
        for combos_elem in root.iter('nr_ca_combos'):
            for combo_elem in combos_elem.iter('ca_combo'):
                if combo_elem.text:
                    combo_text = combo_elem.text.strip()
                    combo = self._parse_combo_string(combo_text, ComboType.NRCA)
                    if combo and len(combo.nr_components) > 0:
                        combos.append(combo)

        return combos

    def _parse_nrdc_combos(self, root: ET.Element) -> List[Combo]:
        """
        Parse NR-DC combos from <nrdc_combos> or similar section.
        """
        combos = []

        for combos_elem in root.iter('nrdc_combos'):
            for combo_elem in combos_elem.iter('ca_combo'):
                if combo_elem.text:
                    combo_text = combo_elem.text.strip()
                    combo = self._parse_combo_string(combo_text, ComboType.NRDC)
                    if combo:
                        combos.append(combo)

        return combos

    def _parse_combo_string(self, combo_str: str, combo_type: ComboType) -> Optional[Combo]:
        """
        Parse a combo string into a Combo object.

        Args:
            combo_str: Raw combo string like "B1A[4];A[1]+N77A[100x4];A[100x1]"
            combo_type: Type of combo (LTE_CA, ENDC, etc.)

        Returns:
            Combo object or None if parsing fails
        """
        components = []
        bcs_set: Set[int] = set()

        # Split by '+' to get individual band entries
        # Handle both '+' and ',' as separators
        band_entries = re.split(r'[+,]', combo_str)

        for entry in band_entries:
            entry = entry.strip()
            if not entry:
                continue

            component = self._parse_band_entry(entry)
            if component:
                components.append(component)

        if not components:
            return None

        return Combo(
            combo_type=combo_type,
            components=components,
            bcs=bcs_set if bcs_set else None,
            raw_string=combo_str,
            source=DataSource.RFC,
        )

    def _parse_band_entry(self, entry: str) -> Optional[BandComponent]:
        """
        Parse a single band entry like "B66A[4];A[1]" or "N77A[100x4];A[100x1]".

        Args:
            entry: Band entry string

        Returns:
            BandComponent or None if parsing fails
        """
        # Pattern to match band entries
        # Examples: B66A, B1A[4], B66A[4];A[1], N77A[100x4], N77A[100x4];A[100x1]
        # Pattern: (B|N)(\d+)([A-Z])(?:\[.*?\])?(?:;[A-Z]\[.*?\])?
        pattern = r'^([BN])(\d+)([A-Z])(?:\[([^\]]*)\])?(?:;([A-Z])(?:\[([^\]]*)\])?)?'

        match = re.match(pattern, entry.strip(), re.IGNORECASE)
        if not match:
            # Try simpler pattern without brackets
            simple_pattern = r'^([BN])(\d+)([A-Z])'
            match = re.match(simple_pattern, entry.strip(), re.IGNORECASE)
            if not match:
                return None

        band_type = match.group(1).upper()  # B or N
        band_num = int(match.group(2))
        band_class = match.group(3).upper()

        # Extract MIMO layers from DL spec like [4] or [100x4]
        mimo_layers = None
        if len(match.groups()) > 3 and match.group(4):
            dl_spec = match.group(4)
            # Try to extract layer count from specs like "4" or "100x4"
            layer_match = re.search(r'x?(\d+)$', dl_spec)
            if layer_match:
                mimo_layers = int(layer_match.group(1))

        return BandComponent(
            band=band_num,
            band_class=band_class,
            mimo_layers=mimo_layers,
            is_nr=(band_type == 'N'),
        )

    def get_parse_errors(self) -> List[str]:
        """Get list of parse errors encountered."""
        return self._parse_errors

    def get_file_info(self) -> Dict[str, str]:
        """Get parsed file info."""
        return self.file_info


def parse_rfc_combos(file_path: str) -> Dict[ComboType, ComboSet]:
    """
    Convenience function to parse RFC XML for combos.

    Args:
        file_path: Path to RFC XML file

    Returns:
        Dict mapping ComboType to ComboSet
    """
    parser = RFCParser()
    return parser.parse(file_path)
