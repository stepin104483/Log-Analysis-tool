"""
UE Capability Parser
Parses UE Capability information to extract bands reported to network.

Expected formats:
1. JSON format from network logs
2. Text format with bandEUTRA, bandNR lists
3. ASN.1 decoded format

Note: Handles 3GPP TS 36.331 Section 6.3.6 for LTE bands 64+:
      - supportedBandListEUTRA covers bands 1-64
      - supportedBandListEUTRA-v9e0 covers bands 65+ (B66, B68, B71, etc.)
      - "64" entries in base list can be placeholders for v9e0 bands
      - Formula: actual B64 count = (count of "64" in base) - (count in v9e0)
"""

import re
import json
from typing import Dict, Set, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class UECapabilityBands:
    """Container for bands extracted from UE Capability"""
    lte_bands: Set[int]       # bandEUTRA / E-UTRA bands (processed with v9e0)
    nr_bands: Set[int]        # NR bands (combined SA/NSA from UE cap)
    nr_sa_bands: Set[int]     # NR SA specific if available
    nr_nsa_bands: Set[int]    # NR NSA specific if available
    raw_data: Dict[str, any]  # Raw extracted data including v9e0 info


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


def extract_lte_bands_with_v9e0(content: str) -> Tuple[Set[int], List[int], List[int]]:
    """
    Extract LTE bands handling v9e0 extension for bands 65+.

    Per 3GPP TS 36.331 Section 6.3.6:
    - supportedBandListEUTRA covers bands 1-64
    - supportedBandListEUTRA-v9e0 covers bands 65+
    - "64" in base list can be placeholder for v9e0 bands

    Args:
        content: UE Capability text content

    Returns:
        Tuple of (final_lte_bands, base_bands_list, v9e0_bands_list)
    """
    final_bands: Set[int] = set()
    base_bands_list: List[int] = []
    v9e0_bands_list: List[int] = []

    # Extract bands from supportedBandListEUTRA (individual bandEUTRA entries)
    # Pattern: "bandEUTRA: 3" or "bandEUTRA 3," or "bandEUTRA 3"
    # Exclude bandEUTRA-v9e0 and bandEUTRA-v1090 patterns
    base_pattern = r'(?<!-)bandEUTRA\s*[:=]?\s*(\d+)'
    base_matches = re.findall(base_pattern, content)

    for match in base_matches:
        try:
            band = int(match)
            if 0 < band <= 64:
                base_bands_list.append(band)
        except ValueError:
            pass

    # Extract bands from supportedBandListEUTRA-v9e0
    # Pattern: "bandEUTRA-v9e0: 66" or "bandEUTRA-v9e0 66"
    v9e0_pattern = r'bandEUTRA-v9e0\s*[:=]?\s*(\d+)'
    v9e0_matches = re.findall(v9e0_pattern, content)

    for match in v9e0_matches:
        try:
            band = int(match)
            if band > 64:  # v9e0 bands should be > 64
                v9e0_bands_list.append(band)
        except ValueError:
            pass

    # Also check for bandEUTRA-v1090 (another extension variant)
    v1090_pattern = r'bandEUTRA-v1090\s*[:=]?\s*(\d+)'
    v1090_matches = re.findall(v1090_pattern, content)

    for match in v1090_matches:
        try:
            band = int(match)
            if band > 64:
                v9e0_bands_list.append(band)
        except ValueError:
            pass

    # Remove duplicates from v9e0 list while preserving order for counting
    seen_v9e0 = set()
    unique_v9e0: List[int] = []
    for band in v9e0_bands_list:
        if band not in seen_v9e0:
            seen_v9e0.add(band)
            unique_v9e0.append(band)
    v9e0_bands_list = unique_v9e0

    # Count "64" entries in base list
    count_64_in_base = base_bands_list.count(64)

    # Add all non-64 bands from base list
    for band in base_bands_list:
        if band != 64:
            final_bands.add(band)

    # Add v9e0 bands (these are bands 65+)
    for band in v9e0_bands_list:
        final_bands.add(band)

    # Determine actual B64 support using the formula
    # actual B64 count = (count of "64" in base) - (count in v9e0)
    actual_b64_count = count_64_in_base - len(v9e0_bands_list)
    if actual_b64_count > 0:
        final_bands.add(64)

    return final_bands, base_bands_list, v9e0_bands_list


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

        # Use the new v9e0-aware LTE band extraction
        lte_bands, base_bands_list, v9e0_bands_list = extract_lte_bands_with_v9e0(content)

        # Store v9e0 info in raw_data for reference
        count_64_in_base = base_bands_list.count(64)
        raw_data['lte_v9e0'] = {
            'base_band_count': len(base_bands_list),
            'count_64_in_base': count_64_in_base,
            'v9e0_bands': v9e0_bands_list,
            'actual_b64_support': count_64_in_base - len(v9e0_bands_list) > 0
        }

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

        # Extract NR bands (individual entries)
        individual_nr = re.findall(r'bandNR\s*[:=]?\s*(\d+)', content)
        for band in individual_nr:
            try:
                nr_bands.add(int(band))
            except ValueError:
                pass

        # Also try pattern-based extraction for NR
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

            # Show v9e0 details if available
            if 'lte_v9e0' in result.raw_data:
                v9e0_info = result.raw_data['lte_v9e0']
                print(f"\nLTE Band 64+ (v9e0 Extension) Details:")
                print(f"  Count of '64' in supportedBandListEUTRA: {v9e0_info['count_64_in_base']}")
                print(f"  Bands in supportedBandListEUTRA-v9e0: {v9e0_info['v9e0_bands']}")
                print(f"  Actual B64 support: {v9e0_info['actual_b64_support']}")
                if v9e0_info['v9e0_bands']:
                    print(f"  Extended bands (65+): {', '.join(f'B{b}' for b in sorted(v9e0_info['v9e0_bands']))}")
    else:
        print("Usage: python ue_capability_parser.py <ue_capability_file>")
        print("\nSupported formats:")
        print("  - JSON with bandEUTRA/bandNR fields")
        print("  - Text with 'LTE Bands: 1, 2, 3' format")
        print("  - ASN.1 decoded with 'bandEUTRA: 1' entries")
        print("\nNote: Handles 3GPP TS 36.331 v9e0 extension for bands 65+")
