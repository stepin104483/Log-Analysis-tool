"""
QXDM Log Parser (0x1CCA)
Parses QXDM 0x1CCA PM RF Band log to extract actual bands on device.

Expected log format:
[0x1CCA] PM RF Band Info
  LTE Bands: 0x00000000 0x0007EFFF 0x00000000 0x00000000
  NR SA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000
  NR NSA Bands: 0x00000000 0x001F0FFF 0x00000000 0x00000000
"""

import re
from typing import Dict, Set, Optional, List
from dataclasses import dataclass


@dataclass
class QXDMBands:
    """Container for bands extracted from QXDM 0x1CCA log"""
    lte_bands: Set[int]
    nr_sa_bands: Set[int]
    nr_nsa_bands: Set[int]
    raw_hex: Dict[str, List[str]]  # Raw hex values from log


def hex_to_bands(hex_values: List[str], start_band: int = 1) -> Set[int]:
    """
    Convert hex bitmask values to band numbers.

    Each hex value represents 32 bands. Bits set to 1 indicate enabled bands.
    Example: 0x00000003 means bands 1 and 2 are enabled (bits 0 and 1)

    Args:
        hex_values: List of hex strings like ['0x00000000', '0x0007EFFF', ...]
        start_band: Starting band number (typically 1)

    Returns:
        Set of enabled band numbers
    """
    bands: Set[int] = set()

    for idx, hex_str in enumerate(hex_values):
        try:
            # Remove '0x' prefix and convert to int
            hex_str = hex_str.strip()
            if hex_str.lower().startswith('0x'):
                hex_str = hex_str[2:]
            value = int(hex_str, 16)

            # Check each bit
            for bit in range(32):
                if value & (1 << bit):
                    band_num = start_band + (idx * 32) + bit
                    bands.add(band_num)

        except ValueError as e:
            print(f"[WARNING] Invalid hex value: {hex_str} - {e}")

    return bands


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

    # Patterns to match different formats of 0x1CCA log
    # Format 1: LTE Bands: 0x00000000 0x0007EFFF 0x00000000 0x00000000
    # Format 2: lte_bands = 0x00000000 0x0007EFFF ...
    # Format 3: LTE: 0x00000000, 0x0007EFFF, ...

    # LTE bands pattern
    lte_patterns = [
        r'LTE\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        r'lte_bands\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        r'EUTRA\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
    ]

    # NR SA bands pattern
    nr_sa_patterns = [
        r'NR\s*SA\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        r'nr5g_sa_bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        r'NR_SA\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
    ]

    # NR NSA bands pattern
    nr_nsa_patterns = [
        r'NR\s*NSA\s*Bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        r'nr5g_nsa_bands?\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
        r'NR_NSA\s*[:=]\s*((?:0x[0-9A-Fa-f]+\s*,?\s*)+)',
    ]

    def extract_hex_values(patterns: List[str], text: str) -> List[str]:
        """Try multiple patterns to extract hex values"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hex_str = match.group(1)
                # Extract all hex values
                hex_values = re.findall(r'0x[0-9A-Fa-f]+', hex_str)
                if hex_values:
                    return hex_values
        return []

    raw_hex['lte'] = extract_hex_values(lte_patterns, content)
    raw_hex['nr_sa'] = extract_hex_values(nr_sa_patterns, content)
    raw_hex['nr_nsa'] = extract_hex_values(nr_nsa_patterns, content)

    # If no structured format found, try to find any 0x1CCA section
    if not any(raw_hex.values()):
        # Look for 0x1CCA marker and parse following lines
        match = re.search(r'0x1CCA.*?(?=0x[0-9A-Fa-f]{4}|\Z)', content, re.DOTALL | re.IGNORECASE)
        if match:
            section = match.group(0)
            raw_hex['lte'] = extract_hex_values(lte_patterns, section)
            raw_hex['nr_sa'] = extract_hex_values(nr_sa_patterns, section)
            raw_hex['nr_nsa'] = extract_hex_values(nr_nsa_patterns, section)

    # Convert hex to bands
    lte_bands = hex_to_bands(raw_hex['lte'])
    nr_sa_bands = hex_to_bands(raw_hex['nr_sa'])
    nr_nsa_bands = hex_to_bands(raw_hex['nr_nsa'])

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
