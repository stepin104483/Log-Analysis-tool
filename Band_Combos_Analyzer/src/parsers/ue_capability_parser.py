"""
UE Capability Parser
Parses UE Capability information to extract bands reported to network.

Expected formats:
1. JSON format from network logs
2. Text format with bandEUTRA, bandNR lists
3. ASN.1 decoded format
"""

import re
import json
from typing import Dict, Set, Optional, List
from dataclasses import dataclass


@dataclass
class UECapabilityBands:
    """Container for bands extracted from UE Capability"""
    lte_bands: Set[int]       # bandEUTRA / E-UTRA bands
    nr_bands: Set[int]        # NR bands (combined SA/NSA from UE cap)
    nr_sa_bands: Set[int]     # NR SA specific if available
    nr_nsa_bands: Set[int]    # NR NSA specific if available
    raw_data: Dict[str, any]  # Raw extracted data


def parse_band_list_text(text: str) -> Set[int]:
    """
    Parse band numbers from text in various formats.

    Handles:
    - Comma separated: "1, 2, 3, 4"
    - Space separated: "1 2 3 4"
    - Bracket list: "[1, 2, 3, 4]"
    - Band prefixed: "B1, B2, B3" or "n1, n2, n3"
    """
    bands: Set[int] = set()

    # Remove brackets
    text = re.sub(r'[\[\]{}()]', '', text)

    # Split by comma or space
    parts = re.split(r'[,\s]+', text)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Remove band prefix (B, n, N, band, etc.)
        part = re.sub(r'^[BbNn](?:and)?', '', part)

        try:
            band_num = int(part)
            if 0 < band_num < 512:  # Reasonable band number range
                bands.add(band_num)
        except ValueError:
            continue

    return bands


def parse_ue_capability_json(content: str) -> Optional[Dict]:
    """Try to parse content as JSON"""
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError:
        return None


def extract_bands_from_json(data: Dict) -> tuple:
    """Extract bands from JSON UE capability data"""
    lte_bands: Set[int] = set()
    nr_bands: Set[int] = set()

    def search_dict(d, path=""):
        nonlocal lte_bands, nr_bands

        if isinstance(d, dict):
            for key, value in d.items():
                key_lower = key.lower()

                # LTE bands
                if 'eutra' in key_lower or 'lte' in key_lower:
                    if 'band' in key_lower:
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, int):
                                    lte_bands.add(item)
                                elif isinstance(item, dict) and 'bandEUTRA' in item:
                                    lte_bands.add(item['bandEUTRA'])

                # NR bands
                elif 'nr' in key_lower and 'band' in key_lower:
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, int):
                                nr_bands.add(item)
                            elif isinstance(item, dict):
                                for k, v in item.items():
                                    if 'band' in k.lower() and isinstance(v, int):
                                        nr_bands.add(v)

                # Recurse
                search_dict(value, f"{path}.{key}")

        elif isinstance(d, list):
            for item in d:
                search_dict(item, path)

    search_dict(data)
    return lte_bands, nr_bands


def parse_ue_capability(file_path: str) -> Optional[UECapabilityBands]:
    """
    Parse UE Capability file.

    Args:
        file_path: Path to UE Capability file (text or JSON)

    Returns:
        UECapabilityBands object, or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] UE Capability file not found: {file_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read UE Capability file: {e}")
        return None

    lte_bands: Set[int] = set()
    nr_bands: Set[int] = set()
    nr_sa_bands: Set[int] = set()
    nr_nsa_bands: Set[int] = set()
    raw_data: Dict[str, any] = {}

    # Try JSON format first
    json_data = parse_ue_capability_json(content)
    if json_data:
        raw_data['format'] = 'json'
        lte_bands, nr_bands = extract_bands_from_json(json_data)
    else:
        # Parse as text format
        raw_data['format'] = 'text'

        # Patterns for LTE bands
        lte_patterns = [
            r'bandEUTRA\s*[:=]\s*([^\n]+)',
            r'supportedBandListEUTRA\s*[:=]\s*([^\n]+)',
            r'E-?UTRA\s*[Bb]ands?\s*[:=]\s*([^\n]+)',
            r'LTE\s*[Bb]ands?\s*[:=]\s*([^\n]+)',
            r'freqBandIndicator\s*[:=]\s*(\d+)',
        ]

        # Patterns for NR bands
        nr_patterns = [
            r'bandNR\s*[:=]\s*([^\n]+)',
            r'supportedBandListNR\s*[:=]\s*([^\n]+)',
            r'NR\s*[Bb]ands?\s*[:=]\s*([^\n]+)',
            r'nr-?FreqBand\s*[:=]\s*([^\n]+)',
        ]

        # NR SA specific
        nr_sa_patterns = [
            r'NR\s*SA\s*[Bb]ands?\s*[:=]\s*([^\n]+)',
            r'sa-?BandList\s*[:=]\s*([^\n]+)',
        ]

        # NR NSA specific
        nr_nsa_patterns = [
            r'NR\s*NSA\s*[Bb]ands?\s*[:=]\s*([^\n]+)',
            r'nsa-?BandList\s*[:=]\s*([^\n]+)',
        ]

        # Extract LTE bands
        for pattern in lte_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                lte_bands.update(parse_band_list_text(match))

        # Extract NR bands
        for pattern in nr_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                nr_bands.update(parse_band_list_text(match))

        # Extract NR SA specific
        for pattern in nr_sa_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                nr_sa_bands.update(parse_band_list_text(match))

        # Extract NR NSA specific
        for pattern in nr_nsa_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                nr_nsa_bands.update(parse_band_list_text(match))

        # Also look for individual band entries (common in ASN.1 decoded logs)
        # Example: "bandEUTRA: 1" or "bandNR: 77"
        individual_lte = re.findall(r'bandEUTRA\s*:\s*(\d+)', content)
        individual_nr = re.findall(r'bandNR\s*:\s*(\d+)', content)

        for band in individual_lte:
            try:
                lte_bands.add(int(band))
            except ValueError:
                pass

        for band in individual_nr:
            try:
                nr_bands.add(int(band))
            except ValueError:
                pass

    # If no SA/NSA split, use combined NR bands
    if not nr_sa_bands and not nr_nsa_bands:
        nr_sa_bands = nr_bands.copy()
        nr_nsa_bands = nr_bands.copy()

    return UECapabilityBands(
        lte_bands=lte_bands,
        nr_bands=nr_bands,
        nr_sa_bands=nr_sa_bands,
        nr_nsa_bands=nr_nsa_bands,
        raw_data=raw_data
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
        result = parse_ue_capability(sys.argv[1])
        if result:
            print(f"\n=== UE Capability Parser Results ===")
            print(f"Format: {result.raw_data.get('format', 'unknown')}")

            print(f"\nExtracted Bands:")
            print(f"  LTE ({len(result.lte_bands)}): {format_bands_display(result.lte_bands, 'B')}")
            print(f"  NR ({len(result.nr_bands)}): {format_bands_display(result.nr_bands, 'n')}")

            if result.nr_sa_bands != result.nr_bands:
                print(f"  NR SA ({len(result.nr_sa_bands)}): {format_bands_display(result.nr_sa_bands, 'n')}")
            if result.nr_nsa_bands != result.nr_bands:
                print(f"  NR NSA ({len(result.nr_nsa_bands)}): {format_bands_display(result.nr_nsa_bands, 'n')}")
    else:
        print("Usage: python ue_capability_parser.py <ue_capability_file>")
        print("\nSupported formats:")
        print("  - JSON with bandEUTRA/bandNR fields")
        print("  - Text with 'LTE Bands: 1, 2, 3' format")
        print("  - ASN.1 decoded with 'bandEUTRA: 1' entries")
