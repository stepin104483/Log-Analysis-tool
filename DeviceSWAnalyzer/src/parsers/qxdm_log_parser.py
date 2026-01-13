"""
QXDM Log Parser (0x1CCA)
Parses QXDM 0x1CCA PM RF Band log to extract actual bands on device.

Supported log formats:

Format 1 (Multi-line with ranges):
    [0x1CCA] PM RF Band Info
    Lte Bands
       Lte Bands 1_64 = 0x000087C0BB08389F
       Lte Bands 65_128 = 0x000000000000004A
    Nr5g Sa Bands
       Nr5g Sa Bands 1_64 = 0x000081A00B0800D7

Format 2 (Single line):
    LTE Bands: 0x00000000 0x0007EFFF 0x00000000 0x00000000
    NR SA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000
"""

import re
from typing import Dict, Set, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class QXDMBands:
    """Container for bands extracted from QXDM 0x1CCA log"""
    lte_bands: Set[int]
    nr_sa_bands: Set[int]
    nr_nsa_bands: Set[int]
    raw_hex: Dict[str, List[str]]  # Raw hex values from log


def hex_to_bands_64bit(hex_value: str, start_band: int) -> Set[int]:
    """
    Convert a 64-bit hex bitmask to band numbers.

    Args:
        hex_value: Hex string like '0x000087C0BB08389F'
        start_band: Starting band number for this hex value

    Returns:
        Set of enabled band numbers
    """
    bands: Set[int] = set()

    try:
        hex_str = hex_value.strip()
        if hex_str.lower().startswith('0x'):
            hex_str = hex_str[2:]
        value = int(hex_str, 16)

        # Check each bit (64 bits)
        for bit in range(64):
            if value & (1 << bit):
                band_num = start_band + bit
                bands.add(band_num)

    except ValueError as e:
        print(f"[WARNING] Invalid hex value: {hex_value} - {e}")

    return bands


def parse_multiline_format(content: str) -> Dict[str, List[Tuple[int, str]]]:
    """
    Parse multi-line format with range indicators like:
       Lte Bands 1_64 = 0x000087C0BB08389F
       Lte Bands 65_128 = 0x000000000000004A

    Returns:
        Dict with 'lte', 'nr_sa', 'nr_nsa' keys, each containing
        list of (start_band, hex_value) tuples
    """
    result: Dict[str, List[Tuple[int, str]]] = {
        'lte': [],
        'nr_sa': [],
        'nr_nsa': []
    }

    # Pattern: "Lte Bands 1_64 = 0xXXXX" or "Nr5g Sa Bands 1_64 = 0xXXXX"
    lte_pattern = r'Lte\s*Bands?\s*(\d+)_\d+\s*=\s*(0x[0-9A-Fa-f]+)'
    nr_sa_pattern = r'Nr5g\s*Sa\s*Bands?\s*(\d+)_\d+\s*=\s*(0x[0-9A-Fa-f]+)'
    nr_nsa_pattern = r'Nr5g\s*Nsa\s*Bands?\s*(\d+)_\d+\s*=\s*(0x[0-9A-Fa-f]+)'

    for match in re.finditer(lte_pattern, content, re.IGNORECASE):
        start_band = int(match.group(1))
        hex_value = match.group(2)
        result['lte'].append((start_band, hex_value))

    for match in re.finditer(nr_sa_pattern, content, re.IGNORECASE):
        start_band = int(match.group(1))
        hex_value = match.group(2)
        result['nr_sa'].append((start_band, hex_value))

    for match in re.finditer(nr_nsa_pattern, content, re.IGNORECASE):
        start_band = int(match.group(1))
        hex_value = match.group(2)
        result['nr_nsa'].append((start_band, hex_value))

    return result


def parse_qxdm_log(file_path: str) -> Optional[QXDMBands]:
    """
    Parse QXDM log file containing 0x1CCA PM RF Band info.

    Args:
        file_path: Path to QXDM log text file

    Returns:
        QXDMBands object, or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] QXDM log file not found: {file_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read QXDM log: {e}")
        return None

    raw_hex: Dict[str, List[str]] = {
        'lte': [],
        'nr_sa': [],
        'nr_nsa': []
    }

    lte_bands: Set[int] = set()
    nr_sa_bands: Set[int] = set()
    nr_nsa_bands: Set[int] = set()

    # Try multi-line format first (Format 1)
    multiline_data = parse_multiline_format(content)

    if any(multiline_data.values()):
        # Process multi-line format
        for start_band, hex_value in multiline_data['lte']:
            raw_hex['lte'].append(hex_value)
            lte_bands.update(hex_to_bands_64bit(hex_value, start_band))

        for start_band, hex_value in multiline_data['nr_sa']:
            raw_hex['nr_sa'].append(hex_value)
            nr_sa_bands.update(hex_to_bands_64bit(hex_value, start_band))

        for start_band, hex_value in multiline_data['nr_nsa']:
            raw_hex['nr_nsa'].append(hex_value)
            nr_nsa_bands.update(hex_to_bands_64bit(hex_value, start_band))

    else:
        # Try single-line format (Format 2)
        lte_patterns = [
            r'LTE\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
            r'lte_bands\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        ]
        nr_sa_patterns = [
            r'NR\s*SA\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
            r'nr5g_sa_bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        ]
        nr_nsa_patterns = [
            r'NR\s*NSA\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
            r'nr5g_nsa_bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        ]

        def extract_hex_values(patterns: List[str], text: str) -> List[str]:
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    hex_str = match.group(1)
                    hex_values = re.findall(r'0x[0-9A-Fa-f]+', hex_str)
                    if hex_values:
                        return hex_values
            return []

        raw_hex['lte'] = extract_hex_values(lte_patterns, content)
        raw_hex['nr_sa'] = extract_hex_values(nr_sa_patterns, content)
        raw_hex['nr_nsa'] = extract_hex_values(nr_nsa_patterns, content)

        # Convert single-line format (assuming 64-bit values, sequential)
        for idx, hex_val in enumerate(raw_hex['lte']):
            start_band = 1 + (idx * 64)
            lte_bands.update(hex_to_bands_64bit(hex_val, start_band))

        for idx, hex_val in enumerate(raw_hex['nr_sa']):
            start_band = 1 + (idx * 64)
            nr_sa_bands.update(hex_to_bands_64bit(hex_val, start_band))

        for idx, hex_val in enumerate(raw_hex['nr_nsa']):
            start_band = 1 + (idx * 64)
            nr_nsa_bands.update(hex_to_bands_64bit(hex_val, start_band))

    return QXDMBands(
        lte_bands=lte_bands,
        nr_sa_bands=nr_sa_bands,
        nr_nsa_bands=nr_nsa_bands,
        raw_hex=raw_hex
    )


def format_bands_display(bands: Set[int], prefix: str = '') -> str:
    """Format band set for display"""
    if not bands:
        return "None"
    sorted_bands = sorted(bands)
    return ', '.join(f"{prefix}{b}" for b in sorted_bands)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = parse_qxdm_log(sys.argv[1])
        if result:
            print(f"\n=== QXDM 0x1CCA Parser Results ===")

            print(f"\nRaw Hex Values:")
            print(f"  LTE: {' '.join(result.raw_hex['lte']) if result.raw_hex['lte'] else 'Not found'}")
            print(f"  NR SA: {' '.join(result.raw_hex['nr_sa']) if result.raw_hex['nr_sa'] else 'Not found'}")
            print(f"  NR NSA: {' '.join(result.raw_hex['nr_nsa']) if result.raw_hex['nr_nsa'] else 'Not found'}")

            print(f"\nDecoded Bands:")
            print(f"  LTE ({len(result.lte_bands)}): {format_bands_display(result.lte_bands, 'B')}")
            print(f"  NR SA ({len(result.nr_sa_bands)}): {format_bands_display(result.nr_sa_bands, 'n')}")
            print(f"  NR NSA ({len(result.nr_nsa_bands)}): {format_bands_display(result.nr_nsa_bands, 'n')}")
    else:
        print("Usage: python qxdm_log_parser.py <qxdm_log.txt>")
        print("\nExpected log format:")
        print("[0x1CCA] PM RF Band Info")
        print("  LTE Bands: 0x00000000 0x0007EFFF 0x00000000 0x00000000")
        print("  NR SA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000")
        print("  NR NSA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000")
