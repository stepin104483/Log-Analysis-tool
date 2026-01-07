"""
RFC (RF Card) XML Parser
Extracts LTE and NR bands from Qualcomm RFC XML files.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Set, Optional
from dataclasses import dataclass


@dataclass
class RFCBands:
    """Container for bands extracted from RFC"""
    lte_bands: Set[int]
    nr_bands: Set[int]
    gsm_bands: Set[str]
    file_info: Dict[str, str]


def parse_band_name(band_name: str) -> tuple:
    """
    Parse band name like 'B1', 'N77', 'B850' into (type, number)
    Returns: (band_type, band_number) or (band_type, band_name) for GSM
    """
    band_name = band_name.strip().upper()

    # LTE bands: B1, B2, B66, etc.
    if band_name.startswith('B'):
        suffix = band_name[1:]
        # Check if it's a GSM band (B850, B900, B1800, B1900)
        if suffix in ['850', '900', '1800', '1900']:
            return ('GSM', band_name)
        try:
            return ('LTE', int(suffix))
        except ValueError:
            return ('UNKNOWN', band_name)

    # NR bands: N1, N77, N78, etc.
    elif band_name.startswith('N'):
        try:
            return ('NR', int(band_name[1:]))
        except ValueError:
            return ('UNKNOWN', band_name)

    # GNSS: L1, L5
    elif band_name.startswith('L'):
        return ('GNSS', band_name)

    return ('UNKNOWN', band_name)


def parse_rfc_xml(file_path: str) -> Optional[RFCBands]:
    """
    Parse RFC XML file and extract all bands.

    Args:
        file_path: Path to RFC XML file

    Returns:
        RFCBands object containing extracted bands, or None if parsing fails
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse RFC XML: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] RFC file not found: {file_path}")
        return None

    lte_bands: Set[int] = set()
    nr_bands: Set[int] = set()
    gsm_bands: Set[str] = set()

    # Extract file info
    file_info = {
        'file_path': file_path,
        'hwid': '',
        'name': ''
    }

    # Try to get card properties
    # Handle namespace in RFC XML
    ns = {'rfc': 'http://www.qualcomm.com/qti/rf/rfc'}

    # Try with namespace first
    card_props = root.find('.//card_properties', ns)
    if card_props is None:
        # Try without namespace
        card_props = root.find('.//card_properties')

    if card_props is not None:
        hwid_elem = card_props.find('hwid', ns) or card_props.find('hwid')
        name_elem = card_props.find('name', ns) or card_props.find('name')

        if hwid_elem is not None and hwid_elem.text:
            file_info['hwid'] = hwid_elem.text.strip()
        if name_elem is not None and name_elem.text:
            file_info['name'] = name_elem.text.strip()

    # Find all band_name elements
    for band_elem in root.iter('band_name'):
        if band_elem.text:
            band_type, band_value = parse_band_name(band_elem.text)

            if band_type == 'LTE' and isinstance(band_value, int):
                lte_bands.add(band_value)
            elif band_type == 'NR' and isinstance(band_value, int):
                nr_bands.add(band_value)
            elif band_type == 'GSM':
                gsm_bands.add(band_value)

    return RFCBands(
        lte_bands=lte_bands,
        nr_bands=nr_bands,
        gsm_bands=gsm_bands,
        file_info=file_info
    )


def format_bands_for_display(bands: Set[int], prefix: str = 'B') -> str:
    """Format band set for display"""
    if not bands:
        return "None"
    sorted_bands = sorted(bands)
    return ', '.join(f"{prefix}{b}" for b in sorted_bands)


if __name__ == "__main__":
    # Test with sample file
    import sys

    if len(sys.argv) > 1:
        result = parse_rfc_xml(sys.argv[1])
        if result:
            print(f"\n=== RFC Parser Results ===")
            print(f"File: {result.file_info.get('name', 'Unknown')}")
            print(f"HWID: {result.file_info.get('hwid', 'Unknown')}")
            print(f"\nLTE Bands ({len(result.lte_bands)}): {format_bands_for_display(result.lte_bands, 'B')}")
            print(f"NR Bands ({len(result.nr_bands)}): {format_bands_for_display(result.nr_bands, 'n')}")
            print(f"GSM Bands ({len(result.gsm_bands)}): {', '.join(sorted(result.gsm_bands)) if result.gsm_bands else 'None'}")
    else:
        print("Usage: python rfc_parser.py <rfc_xml_file>")
