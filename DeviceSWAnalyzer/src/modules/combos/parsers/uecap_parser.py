"""
UE Capability Parser

Parses ASN.1 XML exports of UE Capability information to extract
combo definitions that the device advertises to the network.

Supported capability types:
- EUTRA-Capability: LTE CA combos (supportedBandCombination-r10/r11/r13)
- UE-MRDC-Capability: EN-DC and NR-DC combos
- UE-NR-Capability: NR CA combos
"""

import re
import xml.etree.ElementTree as ET
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


class UECapParser:
    """Parse UE Capability ASN.1 XML exports."""

    def __init__(self):
        self.file_info: Dict[str, str] = {}
        self._parse_errors: List[str] = []
        self._supported_bands: Dict[str, Set[int]] = {'lte': set(), 'nr': set()}

    def parse(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse UE Capability XML and return combo sets.

        Args:
            file_path: Path to UE Capability XML file

        Returns:
            Dict mapping ComboType to ComboSet
        """
        self._parse_errors = []
        self._supported_bands = {'lte': set(), 'nr': set()}

        result = {
            ComboType.LTE_CA: ComboSet(source=DataSource.UE_CAP, combo_type=ComboType.LTE_CA),
            ComboType.ENDC: ComboSet(source=DataSource.UE_CAP, combo_type=ComboType.ENDC),
            ComboType.NRCA: ComboSet(source=DataSource.UE_CAP, combo_type=ComboType.NRCA),
            ComboType.NRDC: ComboSet(source=DataSource.UE_CAP, combo_type=ComboType.NRDC),
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
        except Exception as e:
            self._parse_errors.append(f"Error reading file: {e}")
            return result

        self.file_info['file_path'] = file_path

        # Try different parsing strategies based on XML structure
        # Strategy 1: Parse EUTRA Capability (LTE)
        lte_combos = self._parse_eutra_capability(root)
        for combo in lte_combos:
            result[ComboType.LTE_CA].add(combo)

        # Strategy 2: Parse MRDC Capability (EN-DC, NR-DC)
        mrdc_combos = self._parse_mrdc_capability(root)
        for combo in mrdc_combos:
            if combo.combo_type == ComboType.ENDC:
                result[ComboType.ENDC].add(combo)
            elif combo.combo_type == ComboType.NRDC:
                result[ComboType.NRDC].add(combo)

        # Strategy 3: Parse NR Capability (NR CA)
        nr_combos = self._parse_nr_capability(root)
        for combo in nr_combos:
            result[ComboType.NRCA].add(combo)

        # Strategy 4: Try generic combo parsing for non-standard formats
        if all(len(cs) == 0 for cs in result.values()):
            self._parse_generic_format(root, result)

        return result

    def _parse_eutra_capability(self, root: ET.Element) -> List[Combo]:
        """
        Parse EUTRA (LTE) capability for CA combos.

        Looks for supportedBandCombination elements in various releases.
        """
        combos = []

        # Search patterns for different 3GPP releases
        search_paths = [
            './/supportedBandCombination-r10',
            './/supportedBandCombination-r11',
            './/supportedBandCombination-r13',
            './/supportedBandCombinationAdd-r11',
            './/supportedBandCombinationReduced-r13',
            './/rf-Parameters-v1020/supportedBandCombination-r10',
            './/BandCombinationParameters-r10',
            './/BandCombinationParameters-r13',
        ]

        for path in search_paths:
            for combo_elem in root.iter():
                if self._matches_tag(combo_elem.tag, path.split('/')[-1]):
                    combo = self._parse_lte_band_combination(combo_elem)
                    if combo and len(combo.components) > 0:
                        combos.append(combo)

        # Also try direct iteration for nested structures
        for elem in root.iter():
            tag = self._get_local_tag(elem.tag)
            if 'BandCombinationParameters' in tag:
                combo = self._parse_lte_band_combination(elem)
                if combo and len(combo.components) > 0:
                    # Avoid duplicates
                    if combo.normalized_key not in [c.normalized_key for c in combos]:
                        combos.append(combo)

        return combos

    def _parse_lte_band_combination(self, elem: ET.Element) -> Optional[Combo]:
        """Parse a single LTE band combination element."""
        components = []
        bcs_set: Set[int] = set()

        # Look for band parameters
        for child in elem.iter():
            tag = self._get_local_tag(child.tag)

            # Band parameter elements
            if 'bandParametersDL' in tag or 'BandParametersDL' in tag:
                band_info = self._extract_band_info(child, is_nr=False)
                if band_info:
                    components.append(band_info)

            # Alternative: direct band elements
            elif tag == 'bandEUTRA' or tag == 'bandEUTRA-r10':
                band_num = self._get_int_value(child)
                if band_num:
                    self._supported_bands['lte'].add(band_num)
                    components.append(BandComponent(
                        band=band_num,
                        band_class='A',  # Default if not specified
                        is_nr=False
                    ))

            # BCS (supportedBandwidthCombinationSet)
            elif 'supportedBandwidthCombinationSet' in tag:
                bcs_values = self._extract_bcs(child)
                bcs_set.update(bcs_values)

        if not components:
            return None

        return Combo(
            combo_type=ComboType.LTE_CA,
            components=components,
            bcs=bcs_set if bcs_set else None,
            source=DataSource.UE_CAP,
        )

    def _parse_mrdc_capability(self, root: ET.Element) -> List[Combo]:
        """
        Parse UE-MRDC-Capability for EN-DC and NR-DC combos.

        Looks for supportedBandCombinationList in MRDC capability.
        """
        combos = []

        # Search patterns for MRDC
        for elem in root.iter():
            tag = self._get_local_tag(elem.tag)

            if tag == 'supportedBandCombinationList' or 'BandCombinationList' in tag:
                for combo_elem in elem:
                    combo = self._parse_mrdc_band_combination(combo_elem)
                    if combo:
                        combos.append(combo)

            # Also check for individual BandCombination elements
            elif tag == 'BandCombination' or tag == 'bandCombination':
                combo = self._parse_mrdc_band_combination(elem)
                if combo and combo.normalized_key not in [c.normalized_key for c in combos]:
                    combos.append(combo)

        return combos

    def _parse_mrdc_band_combination(self, elem: ET.Element) -> Optional[Combo]:
        """Parse a single MRDC band combination."""
        components = []
        has_lte = False
        has_nr = False

        for child in elem.iter():
            tag = self._get_local_tag(child.tag)

            # Band parameters in bandList
            if tag == 'BandParameters' or tag == 'bandParameters':
                band_info = self._extract_mrdc_band_params(child)
                if band_info:
                    components.append(band_info)
                    if band_info.is_nr:
                        has_nr = True
                    else:
                        has_lte = True

            # Direct band number elements
            elif tag == 'bandEUTRA':
                band_num = self._get_int_value(child)
                if band_num:
                    self._supported_bands['lte'].add(band_num)
                    components.append(BandComponent(band=band_num, band_class='A', is_nr=False))
                    has_lte = True

            elif tag == 'bandNR' or tag == 'freqBandIndicatorNR':
                band_num = self._get_int_value(child)
                if band_num:
                    self._supported_bands['nr'].add(band_num)
                    components.append(BandComponent(band=band_num, band_class='A', is_nr=True))
                    has_nr = True

        if not components:
            return None

        # Determine combo type
        if has_lte and has_nr:
            combo_type = ComboType.ENDC
        elif has_nr and len(components) > 1:
            combo_type = ComboType.NRDC
        elif has_nr:
            combo_type = ComboType.NRCA
        else:
            combo_type = ComboType.LTE_CA

        return Combo(
            combo_type=combo_type,
            components=components,
            source=DataSource.UE_CAP,
        )

    def _extract_mrdc_band_params(self, elem: ET.Element) -> Optional[BandComponent]:
        """Extract band parameters from MRDC BandParameters element."""
        band_num = None
        band_class = 'A'
        is_nr = False
        mimo = None

        for child in elem.iter():
            tag = self._get_local_tag(child.tag)

            if tag == 'bandEUTRA':
                band_num = self._get_int_value(child)
                is_nr = False
            elif tag == 'bandNR' or tag == 'freqBandIndicatorNR':
                band_num = self._get_int_value(child)
                is_nr = True
            elif 'ca-BandwidthClassDL' in tag or 'bandwidthClassDL' in tag:
                band_class = self._extract_bandwidth_class(child)
            elif 'mimo-ParametersDL' in tag or 'maxNumberMIMO-LayersDL' in tag:
                mimo = self._extract_mimo_layers(child)

        if band_num is None:
            return None

        if is_nr:
            self._supported_bands['nr'].add(band_num)
        else:
            self._supported_bands['lte'].add(band_num)

        return BandComponent(
            band=band_num,
            band_class=band_class,
            mimo_layers=mimo,
            is_nr=is_nr
        )

    def _parse_nr_capability(self, root: ET.Element) -> List[Combo]:
        """
        Parse UE-NR-Capability for NR CA combos.
        """
        combos = []

        for elem in root.iter():
            tag = self._get_local_tag(elem.tag)

            # NR CA specific elements
            if 'supportedBandCombinationList' in tag and 'MRDC' not in str(elem.attrib):
                for combo_elem in elem:
                    combo = self._parse_nr_band_combination(combo_elem)
                    if combo:
                        combos.append(combo)

            elif tag == 'BandCombination-NR' or 'bandCombination-NR' in tag:
                combo = self._parse_nr_band_combination(elem)
                if combo and combo.normalized_key not in [c.normalized_key for c in combos]:
                    combos.append(combo)

        return combos

    def _parse_nr_band_combination(self, elem: ET.Element) -> Optional[Combo]:
        """Parse a single NR band combination."""
        components = []

        for child in elem.iter():
            tag = self._get_local_tag(child.tag)

            if tag == 'bandNR' or tag == 'freqBandIndicatorNR':
                band_num = self._get_int_value(child)
                if band_num:
                    self._supported_bands['nr'].add(band_num)
                    components.append(BandComponent(
                        band=band_num,
                        band_class='A',
                        is_nr=True
                    ))

            elif tag == 'BandParameters' and 'NR' in str(child.attrib):
                band_info = self._extract_mrdc_band_params(child)
                if band_info and band_info.is_nr:
                    components.append(band_info)

        if not components:
            return None

        return Combo(
            combo_type=ComboType.NRCA,
            components=components,
            source=DataSource.UE_CAP,
        )

    def _parse_generic_format(self, root: ET.Element, result: Dict[ComboType, ComboSet]):
        """
        Parse generic/non-standard UE capability formats.

        Looks for common patterns in text content.
        """
        # Get all text content
        text_content = ET.tostring(root, encoding='unicode', method='text')

        # Pattern for band combinations like "1A-3A-7A" or "66A+n77A"
        combo_pattern = re.compile(
            r'([Bb]?\d+[A-Za-z][-+,][Bb]?\d+[A-Za-z](?:[-+,][BbNn]?\d+[A-Za-z])*)',
            re.IGNORECASE
        )

        for match in combo_pattern.finditer(text_content):
            combo_str = match.group(1)
            components = self._parse_combo_string(combo_str)

            if components:
                has_lte = any(not c.is_nr for c in components)
                has_nr = any(c.is_nr for c in components)

                if has_lte and has_nr:
                    combo_type = ComboType.ENDC
                elif has_nr:
                    combo_type = ComboType.NRCA
                else:
                    combo_type = ComboType.LTE_CA

                combo = Combo(
                    combo_type=combo_type,
                    components=components,
                    source=DataSource.UE_CAP,
                    raw_string=combo_str
                )
                result[combo_type].add(combo)

    def _parse_combo_string(self, combo_str: str) -> List[BandComponent]:
        """Parse a combo string like '66A+n77A' into components."""
        components = []
        pattern = re.compile(r'([BbNn]?)(\d+)([A-Za-z])')

        for match in pattern.finditer(combo_str):
            prefix = match.group(1).upper()
            band = int(match.group(2))
            band_class = match.group(3).upper()

            is_nr = prefix == 'N'

            components.append(BandComponent(
                band=band,
                band_class=band_class,
                is_nr=is_nr
            ))

        return components

    def _extract_band_info(self, elem: ET.Element, is_nr: bool) -> Optional[BandComponent]:
        """Extract band information from a band parameters element."""
        band_num = None
        band_class = 'A'
        mimo = None

        for child in elem.iter():
            tag = self._get_local_tag(child.tag)

            if 'bandEUTRA' in tag and not is_nr:
                band_num = self._get_int_value(child)
            elif ('bandNR' in tag or 'freqBandIndicator' in tag) and is_nr:
                band_num = self._get_int_value(child)
            elif 'ca-BandwidthClass' in tag:
                band_class = self._extract_bandwidth_class(child)
            elif 'mimo' in tag.lower():
                mimo = self._extract_mimo_layers(child)

        if band_num is None:
            return None

        return BandComponent(
            band=band_num,
            band_class=band_class,
            mimo_layers=mimo,
            is_nr=is_nr
        )

    def _extract_bandwidth_class(self, elem: ET.Element) -> str:
        """Extract bandwidth class from element."""
        text = elem.text or ''
        text = text.strip().upper()

        # Handle formats like "a", "classA", "bwClass-A"
        if text in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            return text

        match = re.search(r'[A-I]', text, re.IGNORECASE)
        if match:
            return match.group(0).upper()

        return 'A'  # Default

    def _extract_mimo_layers(self, elem: ET.Element) -> Optional[int]:
        """Extract MIMO layers from element."""
        text = elem.text or ''

        # Try to find a number
        match = re.search(r'(\d+)', text)
        if match:
            layers = int(match.group(1))
            if 1 <= layers <= 8:
                return layers

        # Check for named values like "twoLayers", "fourLayers"
        layer_map = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8
        }
        text_lower = text.lower()
        for name, value in layer_map.items():
            if name in text_lower:
                return value

        return None

    def _extract_bcs(self, elem: ET.Element) -> Set[int]:
        """Extract BCS values from element."""
        bcs = set()
        text = elem.text or ''

        # Parse comma-separated or space-separated values
        for part in re.split(r'[,\s]+', text):
            try:
                bcs.add(int(part.strip()))
            except ValueError:
                continue

        return bcs

    def _get_int_value(self, elem: ET.Element) -> Optional[int]:
        """Get integer value from element text."""
        if elem.text:
            try:
                return int(elem.text.strip())
            except ValueError:
                pass
        return None

    def _get_local_tag(self, tag: str) -> str:
        """Remove namespace from tag."""
        if '}' in tag:
            return tag.split('}')[1]
        return tag

    def _matches_tag(self, tag: str, pattern: str) -> bool:
        """Check if tag matches pattern (ignoring namespace)."""
        local_tag = self._get_local_tag(tag)
        return pattern.lower() in local_tag.lower()

    def get_parse_errors(self) -> List[str]:
        """Get list of parse errors encountered."""
        return self._parse_errors

    def get_file_info(self) -> Dict[str, str]:
        """Get parsed file info."""
        return self.file_info

    def get_supported_bands(self) -> Dict[str, Set[int]]:
        """Get all supported bands found in the capability."""
        return self._supported_bands


def parse_uecap_combos(file_path: str) -> Dict[ComboType, ComboSet]:
    """
    Convenience function to parse UE Capability XML for combos.

    Args:
        file_path: Path to UE Capability XML file

    Returns:
        Dict mapping ComboType to ComboSet
    """
    parser = UECapParser()
    return parser.parse(file_path)
