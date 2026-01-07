"""
Hardware Band Filtering XML Parser
Parses hardware_band_filtering.xml to extract allowed band ranges.

Note: HW Filter uses 0-indexed bands (0 = Band 1, 1 = Band 2, etc.)
"""

import xml.etree.ElementTree as ET
from typing import Dict, Set, Optional, List
from dataclasses import dataclass


@dataclass
class HWFilterBands:
    """Container for bands extracted from HW Band Filtering"""
    gw_bands: Set[int]      # GSM/WCDMA bands (0-indexed)
    lte_bands: Set[int]     # LTE bands (0-indexed in file, converted to 1-indexed)
    nr_sa_bands: Set[int]   # NR SA bands (actual band numbers)
    nr_nsa_bands: Set[int]  # NR NSA bands (actual band numbers)
    tds_bands: Set[int]     # TD-SCDMA bands
    raw_ranges: Dict[str, str]  # Raw range strings from XML


def parse_range_string(range_str: str) -> Set[int]:
    """
    Parse range string like "0-10 14-16 18-28 30-32" into a set of integers.

    Args:
        range_str: Space-separated ranges (e.g., "0-10 14-16 30")

    Returns:
        Set of all integers in the ranges
    """
    result: Set[int] = set()

    if not range_str or not range_str.strip():
        return result

    parts = range_str.strip().split()

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if '-' in part:
            # Range like "0-10"
            try:
                start, end = part.split('-', 1)
                start_num = int(start.strip())
                end_num = int(end.strip())
                result.update(range(start_num, end_num + 1))
            except ValueError:
                print(f"[WARNING] Invalid range format: {part}")
        else:
            # Single number
            try:
                result.add(int(part))
            except ValueError:
                print(f"[WARNING] Invalid number: {part}")

    return result


def convert_0indexed_to_bands(indices: Set[int]) -> Set[int]:
    """
    Convert 0-indexed band positions to actual band numbers.
    In HW filter: index 0 = Band 1, index 1 = Band 2, etc.

    Args:
        indices: Set of 0-indexed positions

    Returns:
        Set of actual band numbers (1-indexed)
    """
    return {idx + 1 for idx in indices}


def parse_hw_filter_xml(file_path: str) -> Optional[HWFilterBands]:
    """
    Parse hardware_band_filtering.xml file.

    Args:
        file_path: Path to hardware_band_filtering.xml

    Returns:
        HWFilterBands object containing allowed bands, or None if parsing fails
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse HW Filter XML: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] HW Filter file not found: {file_path}")
        return None

    raw_ranges: Dict[str, str] = {}

    # Parse each band type
    gw_elem = root.find('gw_bands')
    tds_elem = root.find('tds_bands')
    lte_elem = root.find('lte_bands')
    nr_sa_elem = root.find('nr5g_sa_bands')
    nr_nsa_elem = root.find('nr5g_nsa_bands')

    # Extract raw ranges
    raw_ranges['gw_bands'] = gw_elem.text if gw_elem is not None and gw_elem.text else ''
    raw_ranges['tds_bands'] = tds_elem.text if tds_elem is not None and tds_elem.text else ''
    raw_ranges['lte_bands'] = lte_elem.text if lte_elem is not None and lte_elem.text else ''
    raw_ranges['nr5g_sa_bands'] = nr_sa_elem.text if nr_sa_elem is not None and nr_sa_elem.text else ''
    raw_ranges['nr5g_nsa_bands'] = nr_nsa_elem.text if nr_nsa_elem is not None and nr_nsa_elem.text else ''

    # Parse ranges to sets
    gw_indices = parse_range_string(raw_ranges['gw_bands'])
    tds_indices = parse_range_string(raw_ranges['tds_bands'])
    lte_indices = parse_range_string(raw_ranges['lte_bands'])
    nr_sa_indices = parse_range_string(raw_ranges['nr5g_sa_bands'])
    nr_nsa_indices = parse_range_string(raw_ranges['nr5g_nsa_bands'])

    # Convert LTE from 0-indexed to actual band numbers
    # HW filter uses 0-indexed: index 0 = B1, index 6 = B7, etc.
    lte_bands = convert_0indexed_to_bands(lte_indices)

    # NR bands in HW filter appear to be actual band numbers (not 0-indexed)
    # But we need to verify - for now, use as-is since ranges like "0-10" suggest 0-indexed
    # Converting to actual bands: index 0 = n1, index 76 = n77, etc.
    nr_sa_bands = convert_0indexed_to_bands(nr_sa_indices)
    nr_nsa_bands = convert_0indexed_to_bands(nr_nsa_indices)

    return HWFilterBands(
        gw_bands=gw_indices,
        lte_bands=lte_bands,
        nr_sa_bands=nr_sa_bands,
        nr_nsa_bands=nr_nsa_bands,
        tds_bands=tds_indices,
        raw_ranges=raw_ranges
    )


def is_band_allowed(band_num: int, allowed_bands: Set[int]) -> bool:
    """
    Check if a band number is in the allowed set.

    Args:
        band_num: The band number to check (1-indexed)
        allowed_bands: Set of allowed band numbers

    Returns:
        True if band is allowed, False otherwise
    """
    return band_num in allowed_bands


def format_bands_summary(bands: Set[int], max_display: int = 20) -> str:
    """Format band set for display with optional truncation"""
    if not bands:
        return "None"
    sorted_bands = sorted(bands)
    if len(sorted_bands) > max_display:
        displayed = sorted_bands[:max_display]
        return f"{', '.join(map(str, displayed))}... ({len(sorted_bands)} total)"
    return ', '.join(map(str, sorted_bands))


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = parse_hw_filter_xml(sys.argv[1])
        if result:
            print(f"\n=== HW Band Filter Parser Results ===")
            print(f"\nRaw Ranges:")
            for key, value in result.raw_ranges.items():
                print(f"  {key}: {value[:80]}..." if len(value) > 80 else f"  {key}: {value}")

            print(f"\nParsed Bands (converted to 1-indexed):")
            print(f"  LTE Bands: {format_bands_summary(result.lte_bands)}")
            print(f"  NR SA Bands: {format_bands_summary(result.nr_sa_bands)}")
            print(f"  NR NSA Bands: {format_bands_summary(result.nr_nsa_bands)}")
            print(f"  GW Bands: {format_bands_summary(result.gw_bands)}")
    else:
        print("Usage: python hw_filter_parser.py <hw_band_filtering.xml>")
