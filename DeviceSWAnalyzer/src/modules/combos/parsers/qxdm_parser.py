"""
QXDM Log Parser for 0xB826 (NR5G RRC Supported CA Combos)

Parses QXDM text exports of 0xB826 log packets to extract combo information.

0xB826 Log Structure:
- Header: Version, Subscription ID, Number of Records
- Per-Record: Combo Index, RAT Type, Band, BW Class, MIMO layers

Supported formats:
- QXDM text export (.txt)
- ISLOG text conversion
- HDFV viewer export
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict

from ..models import (
    ComboType,
    DataSource,
    BandComponent,
    Combo,
    ComboSet,
)


class QXDMParser:
    """Parse QXDM 0xB826 logs for RRC table combos."""

    def __init__(self):
        self.file_info: Dict[str, str] = {}
        self._parse_errors: List[str] = []
        self._raw_combos: Dict[int, List[Dict]] = defaultdict(list)  # combo_index -> band entries

    def parse(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse QXDM 0xB826 log and return combo sets.

        Args:
            file_path: Path to QXDM text export file

        Returns:
            Dict mapping ComboType to ComboSet
        """
        self._parse_errors = []
        self._raw_combos = defaultdict(list)

        result = {
            ComboType.LTE_CA: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.LTE_CA),
            ComboType.ENDC: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.ENDC),
            ComboType.NRCA: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.NRCA),
            ComboType.NRDC: ComboSet(source=DataSource.RRC_TABLE, combo_type=ComboType.NRDC),
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except FileNotFoundError:
            self._parse_errors.append(f"File not found: {file_path}")
            return result
        except Exception as e:
            self._parse_errors.append(f"Error reading file: {e}")
            return result

        self.file_info['file_path'] = file_path

        # Try different parsing strategies
        if self._parse_structured_format(content):
            pass
        elif self._parse_table_format(content):
            pass
        elif self._parse_raw_format(content):
            pass
        else:
            self._parse_errors.append("Could not parse log format")

        # Convert raw combos to Combo objects
        self._build_combo_sets(result)

        return result

    def _parse_structured_format(self, content: str) -> bool:
        """
        Parse structured QXDM export format with clear field labels.

        Example format:
            Combo Index = 0
            Number of Bands = 2
            [Band 0]
            RAT Type = LTE
            Band = 66
            DL BW Class = A
            UL BW Class = A
            DL MIMO = 4
            [Band 1]
            RAT Type = NR
            Band = 77
            ...
        """
        # Check if this format is present
        if 'Combo Index' not in content and 'combo_index' not in content.lower():
            return False

        current_combo_idx = None
        current_band = {}

        # Patterns for structured format
        combo_idx_pattern = re.compile(r'Combo\s*Index\s*[=:]\s*(\d+)', re.IGNORECASE)
        rat_pattern = re.compile(r'RAT\s*(?:Type)?\s*[=:]\s*(\w+)', re.IGNORECASE)
        band_pattern = re.compile(r'(?:^|\s)Band\s*[=:]\s*(\d+)', re.IGNORECASE)
        dl_bw_pattern = re.compile(r'DL\s*(?:BW\s*)?Class\s*[=:]\s*(\w)', re.IGNORECASE)
        ul_bw_pattern = re.compile(r'UL\s*(?:BW\s*)?Class\s*[=:]\s*(\w)', re.IGNORECASE)
        dl_mimo_pattern = re.compile(r'DL\s*(?:MIMO|Layers?)\s*[=:]\s*(\d+)', re.IGNORECASE)

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check for new combo
            combo_match = combo_idx_pattern.search(line)
            if combo_match:
                # Save previous band if exists
                if current_band and current_combo_idx is not None:
                    self._raw_combos[current_combo_idx].append(current_band.copy())
                    current_band = {}

                current_combo_idx = int(combo_match.group(1))
                continue

            if current_combo_idx is None:
                continue

            # Check for band header (indicates new band in combo)
            if re.search(r'\[Band\s*\d+\]', line, re.IGNORECASE):
                if current_band:
                    self._raw_combos[current_combo_idx].append(current_band.copy())
                    current_band = {}
                continue

            # Parse band fields
            rat_match = rat_pattern.search(line)
            if rat_match:
                current_band['rat'] = rat_match.group(1).upper()

            band_match = band_pattern.search(line)
            if band_match:
                current_band['band'] = int(band_match.group(1))

            dl_bw_match = dl_bw_pattern.search(line)
            if dl_bw_match:
                current_band['dl_class'] = dl_bw_match.group(1).upper()

            ul_bw_match = ul_bw_pattern.search(line)
            if ul_bw_match:
                current_band['ul_class'] = ul_bw_match.group(1).upper()

            dl_mimo_match = dl_mimo_pattern.search(line)
            if dl_mimo_match:
                current_band['mimo'] = int(dl_mimo_match.group(1))

        # Save last band
        if current_band and current_combo_idx is not None:
            self._raw_combos[current_combo_idx].append(current_band.copy())

        return len(self._raw_combos) > 0

    def _parse_table_format(self, content: str) -> bool:
        """
        Parse table format with columns.

        Example:
            Index | RAT  | Band | DL BW | UL BW | DL MIMO | UL MIMO
            ------|------|------|-------|-------|---------|--------
              0   | LTE  |  66  |   A   |   A   |    4    |    1
              0   | NR   |  77  |   A   |   A   |    4    |    1
              1   | LTE  |   2  |   A   |   A   |    4    |    1
        """
        # Look for table header pattern
        header_pattern = re.compile(
            r'Index.*RAT.*Band.*(?:BW|Class)',
            re.IGNORECASE
        )

        if not header_pattern.search(content):
            return False

        # Pattern for table rows: index | rat | band | dl_class | ul_class | dl_mimo | ul_mimo
        row_pattern = re.compile(
            r'^\s*(\d+)\s*\|?\s*(LTE|NR|EUTRA|NR5G)\s*\|?\s*(\d+)\s*\|?\s*([A-Z])\s*\|?\s*([A-Z])?\s*\|?\s*(\d+)?',
            re.IGNORECASE | re.MULTILINE
        )

        for match in row_pattern.finditer(content):
            combo_idx = int(match.group(1))
            rat = match.group(2).upper()
            band = int(match.group(3))
            dl_class = match.group(4).upper()
            ul_class = match.group(5).upper() if match.group(5) else dl_class
            mimo = int(match.group(6)) if match.group(6) else None

            # Normalize RAT type
            if rat in ['EUTRA', 'LTE']:
                rat = 'LTE'
            elif rat in ['NR5G', 'NR']:
                rat = 'NR'

            band_entry = {
                'rat': rat,
                'band': band,
                'dl_class': dl_class,
                'ul_class': ul_class,
            }
            if mimo:
                band_entry['mimo'] = mimo

            self._raw_combos[combo_idx].append(band_entry)

        return len(self._raw_combos) > 0

    def _parse_raw_format(self, content: str) -> bool:
        """
        Parse raw/freeform format by looking for combo patterns.

        Looks for patterns like:
        - DC_66A_n77A (EN-DC combo notation)
        - 1A-3A-7A (LTE CA notation)
        - eutra-CA: 1A+3A BCS=0
        - ENDC: B66A+N77A
        """
        # Pattern for DC_xxA_nyyA format (EN-DC)
        endc_pattern = re.compile(
            r'DC[_-]?(\d+)([A-Z])[_-]?n(\d+)([A-Z])',
            re.IGNORECASE
        )

        # Pattern for combo string format: B66A+N77A or 66A-77A
        combo_string_pattern = re.compile(
            r'([BN]?)(\d+)([A-Z])(?:[_\-+,]([BN]?)(\d+)([A-Z]))+',
            re.IGNORECASE
        )

        # Pattern for labeled combos: ENDC: B66A+N77A, LTE-CA: 1A+3A
        labeled_pattern = re.compile(
            r'(ENDC|EN-DC|LTE[-_]?CA|NRCA|NR[-_]?CA|NRDC|NR[-_]?DC)\s*[:=]\s*(.+)',
            re.IGNORECASE
        )

        combo_idx = 0

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check for DC_xxA_nyyA format
            endc_match = endc_pattern.search(line)
            if endc_match:
                lte_band = int(endc_match.group(1))
                lte_class = endc_match.group(2).upper()
                nr_band = int(endc_match.group(3))
                nr_class = endc_match.group(4).upper()

                self._raw_combos[combo_idx].append({
                    'rat': 'LTE', 'band': lte_band, 'dl_class': lte_class
                })
                self._raw_combos[combo_idx].append({
                    'rat': 'NR', 'band': nr_band, 'dl_class': nr_class
                })
                combo_idx += 1
                continue

            # Check for labeled combos
            labeled_match = labeled_pattern.search(line)
            if labeled_match:
                combo_type_str = labeled_match.group(1).upper()
                combo_str = labeled_match.group(2)

                bands = self._extract_bands_from_string(combo_str)
                if bands:
                    for band_entry in bands:
                        self._raw_combos[combo_idx].append(band_entry)
                    combo_idx += 1
                continue

        return len(self._raw_combos) > 0

    def _extract_bands_from_string(self, combo_str: str) -> List[Dict]:
        """Extract band entries from a combo string like B66A+N77A or 1A-3A-7A."""
        bands = []

        # Pattern: (B|N|empty)(band_number)(class)
        pattern = re.compile(r'([BN]?)(\d+)([A-Z])', re.IGNORECASE)

        for match in pattern.finditer(combo_str):
            prefix = match.group(1).upper()
            band = int(match.group(2))
            band_class = match.group(3).upper()

            # Determine RAT type
            if prefix == 'N':
                rat = 'NR'
            elif prefix == 'B':
                rat = 'LTE'
            else:
                # No prefix - assume NR if band > 256, else LTE
                rat = 'NR' if band > 256 else 'LTE'

            bands.append({
                'rat': rat,
                'band': band,
                'dl_class': band_class
            })

        return bands

    def _build_combo_sets(self, result: Dict[ComboType, ComboSet]):
        """Convert raw combos to Combo objects and categorize by type."""
        for combo_idx, band_entries in self._raw_combos.items():
            if not band_entries:
                continue

            components = []
            has_lte = False
            has_nr = False

            for entry in band_entries:
                rat = entry.get('rat', 'LTE')
                band = entry.get('band')
                dl_class = entry.get('dl_class', 'A')
                mimo = entry.get('mimo')

                if band is None:
                    continue

                is_nr = (rat == 'NR')
                if is_nr:
                    has_nr = True
                else:
                    has_lte = True

                component = BandComponent(
                    band=band,
                    band_class=dl_class,
                    mimo_layers=mimo,
                    is_nr=is_nr
                )
                components.append(component)

            if not components:
                continue

            # Determine combo type
            if has_lte and has_nr:
                combo_type = ComboType.ENDC
            elif has_lte and len(components) > 1:
                combo_type = ComboType.LTE_CA
            elif has_nr and len(components) > 1:
                combo_type = ComboType.NRCA
            elif has_nr:
                combo_type = ComboType.NRCA  # Single NR band
            else:
                combo_type = ComboType.LTE_CA  # Single LTE band

            combo = Combo(
                combo_type=combo_type,
                components=components,
                source=DataSource.RRC_TABLE,
                raw_string=f"combo_{combo_idx}"
            )

            result[combo_type].add(combo)

    def get_parse_errors(self) -> List[str]:
        """Get list of parse errors encountered."""
        return self._parse_errors

    def get_file_info(self) -> Dict[str, str]:
        """Get parsed file info."""
        return self.file_info

    def get_combo_count(self) -> int:
        """Get total number of unique combos parsed."""
        return len(self._raw_combos)


def parse_qxdm_combos(file_path: str) -> Dict[ComboType, ComboSet]:
    """
    Convenience function to parse QXDM 0xB826 log for combos.

    Args:
        file_path: Path to QXDM text export file

    Returns:
        Dict mapping ComboType to ComboSet
    """
    parser = QXDMParser()
    return parser.parse(file_path)
