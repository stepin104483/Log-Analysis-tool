"""
Generic Band Restrictions XML Parser
Parses generic_band_restrictions.xml for regulatory (FCC, etc.) band exclusions.

Note: Generic Restrictions uses 0-indexed bands (0 = Band 1, 6 = Band 7, etc.)
      All band numbers are converted to 1-indexed (actual band numbers) during parsing.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Set, Optional, List
from dataclasses import dataclass


@dataclass
class GenericRestrictionBands:
    """Container for bands extracted from Generic Restrictions"""
    policy_name: str
    policy_version: str
    # FCC compliant exclusions - converted to 1-indexed
    lte_excluded: Set[int]
    nr_sa_excluded: Set[int]
    nr_nsa_excluded: Set[int]
    gw_excluded: Set[int]
    # MCC lists for regional restrictions
    mcc_lists: Dict[str, List[str]]
    # All restriction configs (raw 0-indexed values)
    restriction_configs: Dict[str, Dict]


def convert_0indexed_to_bands(indices: Set[int]) -> Set[int]:
    """
    Convert 0-indexed band positions to actual band numbers.
    Generic Restrictions uses 0-indexed: value 0 = Band 1, value 6 = Band 7, etc.

    Args:
        indices: Set of 0-indexed values from generic restrictions

    Returns:
        Set of actual band numbers (1-indexed)
    """
    return {idx + 1 for idx in indices}


def parse_band_numbers_raw(text: str) -> Set[int]:
    """Parse space-separated band numbers (raw 0-indexed values)"""
    result: Set[int] = set()
    if not text or not text.strip():
        return result

    for part in text.strip().split():
        try:
            result.add(int(part.strip()))
        except ValueError:
            continue

    return result


def parse_band_numbers(text: str) -> Set[int]:
    """
    Parse space-separated band numbers and convert to 1-indexed.

    Args:
        text: Space-separated 0-indexed numbers

    Returns:
        Set of actual band numbers (1-indexed)
    """
    raw_values = parse_band_numbers_raw(text)
    return convert_0indexed_to_bands(raw_values)


def parse_rf_band_list(elem: ET.Element) -> Dict:
    """Parse an rf_band_list element for restrictions"""
    result = {}

    for band_type in ['gw_bands', 'lte_bands', 'tds_bands', 'nr5g_sa_bands', 'nr5g_nsa_bands']:
        band_elem = elem.find(band_type)
        if band_elem is not None:
            band_info = {
                'base': band_elem.get('base', 'current'),
                'exclude': set(),
                'include': set()
            }

            exclude_elem = band_elem.find('exclude')
            if exclude_elem is not None and exclude_elem.text:
                band_info['exclude'] = parse_band_numbers(exclude_elem.text)

            include_elem = band_elem.find('include')
            if include_elem is not None and include_elem.text:
                band_info['include'] = parse_band_numbers(include_elem.text)

            result[band_type] = band_info

    return result


def parse_generic_restriction_xml(file_path: str) -> Optional[GenericRestrictionBands]:
    """
    Parse generic_band_restrictions.xml file.

    Args:
        file_path: Path to generic_band_restrictions.xml

    Returns:
        GenericRestrictionBands object, or None if parsing fails
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse Generic Restrictions XML: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] Generic Restrictions file not found: {file_path}")
        return None

    policy_name = root.get('name', 'Unknown')
    policy_version = root.get('policy_ver', 'Unknown')

    # Parse MCC lists
    mcc_lists: Dict[str, List[str]] = {}
    for mcc_elem in root.iter('mcc_list'):
        list_name = mcc_elem.get('name', '')
        ns = mcc_elem.get('ns', '')
        full_name = f"{ns}:{list_name}" if ns else list_name
        if full_name and mcc_elem.text:
            mcc_lists[full_name] = mcc_elem.text.strip().split()

    # Parse all rf_band_list elements
    restriction_configs: Dict[str, Dict] = {}
    for band_list in root.iter('rf_band_list'):
        list_name = band_list.get('name', 'unnamed')
        ns = band_list.get('ns', '')
        full_name = f"{ns}:{list_name}" if ns else list_name
        restriction_configs[full_name] = parse_rf_band_list(band_list)

    # Extract FCC compliant exclusions (US market)
    lte_excluded: Set[int] = set()
    nr_sa_excluded: Set[int] = set()
    nr_nsa_excluded: Set[int] = set()
    gw_excluded: Set[int] = set()

    # Look for fcc_compliant or us-related restrictions
    for config_name, config in restriction_configs.items():
        if 'fcc' in config_name.lower() or 'us' in config_name.lower():
            if 'lte_bands' in config:
                lte_excluded.update(config['lte_bands'].get('exclude', set()))
            if 'nr5g_sa_bands' in config:
                nr_sa_excluded.update(config['nr5g_sa_bands'].get('exclude', set()))
            if 'nr5g_nsa_bands' in config:
                nr_nsa_excluded.update(config['nr5g_nsa_bands'].get('exclude', set()))
            if 'gw_bands' in config:
                gw_excluded.update(config['gw_bands'].get('exclude', set()))

        # Also check for GSM disable configs
        if 'gsm' in config_name.lower() or 'disable' in config_name.lower():
            if 'gw_bands' in config:
                gw_excluded.update(config['gw_bands'].get('exclude', set()))

    return GenericRestrictionBands(
        policy_name=policy_name,
        policy_version=policy_version,
        lte_excluded=lte_excluded,
        nr_sa_excluded=nr_sa_excluded,
        nr_nsa_excluded=nr_nsa_excluded,
        gw_excluded=gw_excluded,
        mcc_lists=mcc_lists,
        restriction_configs=restriction_configs
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = parse_generic_restriction_xml(sys.argv[1])
        if result:
            print(f"\n=== Generic Restriction Parser Results ===")
            print(f"Policy: {result.policy_name}")
            print(f"Version: {result.policy_version}")
            print(f"\n(Note: All bands converted from 0-indexed to actual band numbers)")

            print(f"\nMCC Lists:")
            for name, mccs in result.mcc_lists.items():
                print(f"  {name}: {' '.join(mccs)}")

            print(f"\nFCC/Regulatory Excluded Bands (converted to 1-indexed):")
            print(f"  LTE: {sorted(result.lte_excluded) if result.lte_excluded else 'None'}")
            print(f"  NR SA: {sorted(result.nr_sa_excluded) if result.nr_sa_excluded else 'None'}")
            print(f"  NR NSA: {sorted(result.nr_nsa_excluded) if result.nr_nsa_excluded else 'None'}")
            print(f"  GW: {sorted(result.gw_excluded) if result.gw_excluded else 'None'}")

            print(f"\nRestriction Configs Found: {list(result.restriction_configs.keys())}")
    else:
        print("Usage: python generic_restriction_parser.py <generic_band_restrictions.xml>")
