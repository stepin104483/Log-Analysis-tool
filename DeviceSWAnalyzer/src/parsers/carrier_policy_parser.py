"""
Carrier Policy XML Parser
Parses carrier_policy.xml to extract band exclusions and inclusions per carrier.

Note: Carrier Policy uses 0-indexed bands (0 = Band 1, 6 = Band 7, etc.)
      All band numbers are converted to 1-indexed (actual band numbers) during parsing.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field


@dataclass
class CarrierPolicyBands:
    """Container for bands extracted from Carrier Policy"""
    carrier_name: str
    policy_version: str
    # Excluded bands (bands that are filtered out) - converted to 1-indexed
    gw_excluded: Set[int]
    lte_excluded: Set[int]
    nr_sa_excluded: Set[int]
    nr_nsa_excluded: Set[int]
    # Included bands (for roaming configs where base="none") - converted to 1-indexed
    nr_sa_included: Set[int]
    nr_nsa_included: Set[int]
    # MCC lists
    mcc_lists: Dict[str, List[str]]
    # Raw band list configs (raw 0-indexed values)
    band_lists: Dict[str, Dict]


def convert_0indexed_to_bands(indices: Set[int]) -> Set[int]:
    """
    Convert 0-indexed band positions to actual band numbers.
    Carrier Policy uses 0-indexed: value 0 = Band 1, value 6 = Band 7, etc.

    Args:
        indices: Set of 0-indexed values from carrier policy

    Returns:
        Set of actual band numbers (1-indexed)
    """
    return {idx + 1 for idx in indices}


def parse_band_numbers_raw(text: str) -> Set[int]:
    """
    Parse space-separated band numbers (raw 0-indexed values).

    Args:
        text: Space-separated numbers like "6 7 8 15 16 17 18 19 20"

    Returns:
        Set of raw 0-indexed values
    """
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
        text: Space-separated 0-indexed numbers like "6 7 8 15 16 17 18 19 20"

    Returns:
        Set of actual band numbers (1-indexed)
    """
    raw_values = parse_band_numbers_raw(text)
    return convert_0indexed_to_bands(raw_values)


def parse_rf_band_list(elem: ET.Element) -> Dict:
    """
    Parse an rf_band_list element.

    Returns:
        Dict with 'base', 'exclude', 'include' for each band type
    """
    result = {}

    for band_type in ['gw_bands', 'lte_bands', 'tds_bands', 'nr5g_sa_bands', 'nr5g_nsa_bands']:
        band_elem = elem.find(band_type)
        if band_elem is not None:
            band_info = {
                'base': band_elem.get('base', 'current'),
                'exclude': set(),
                'include': set()
            }

            # Check for exclude element
            exclude_elem = band_elem.find('exclude')
            if exclude_elem is not None and exclude_elem.text:
                band_info['exclude'] = parse_band_numbers(exclude_elem.text)

            # Check for include element
            include_elem = band_elem.find('include')
            if include_elem is not None and include_elem.text:
                band_info['include'] = parse_band_numbers(include_elem.text)

            result[band_type] = band_info

    return result


def parse_carrier_policy_xml(file_path: str) -> Optional[CarrierPolicyBands]:
    """
    Parse carrier_policy.xml file.

    Args:
        file_path: Path to carrier_policy.xml

    Returns:
        CarrierPolicyBands object, or None if parsing fails
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse Carrier Policy XML: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] Carrier Policy file not found: {file_path}")
        return None

    # Get policy attributes
    carrier_name = root.get('name', 'Unknown')
    policy_version = root.get('policy_ver', 'Unknown')

    # Parse MCC lists
    mcc_lists: Dict[str, List[str]] = {}
    for mcc_elem in root.iter('mcc_list'):
        list_name = mcc_elem.get('name', '')
        if list_name and mcc_elem.text:
            mcc_lists[list_name] = mcc_elem.text.strip().split()

    # Parse all rf_band_list elements
    band_lists: Dict[str, Dict] = {}
    for band_list in root.iter('rf_band_list'):
        list_name = band_list.get('name', 'unnamed')
        band_lists[list_name] = parse_rf_band_list(band_list)

    # Extract exclusions (typically from home config)
    gw_excluded: Set[int] = set()
    lte_excluded: Set[int] = set()
    nr_sa_excluded: Set[int] = set()
    nr_nsa_excluded: Set[int] = set()
    nr_sa_included: Set[int] = set()
    nr_nsa_included: Set[int] = set()

    # Look for rf_bands_home or similar
    for list_name, bands_config in band_lists.items():
        if 'home' in list_name.lower():
            # Home config - extract exclusions
            if 'gw_bands' in bands_config:
                gw_excluded.update(bands_config['gw_bands'].get('exclude', set()))
            if 'lte_bands' in bands_config:
                lte_excluded.update(bands_config['lte_bands'].get('exclude', set()))
            if 'nr5g_sa_bands' in bands_config:
                nr_sa_excluded.update(bands_config['nr5g_sa_bands'].get('exclude', set()))
            if 'nr5g_nsa_bands' in bands_config:
                nr_nsa_excluded.update(bands_config['nr5g_nsa_bands'].get('exclude', set()))

        elif 'roam' in list_name.lower():
            # Roaming config - if base="none", these are explicit includes
            if 'nr5g_sa_bands' in bands_config:
                if bands_config['nr5g_sa_bands'].get('base') == 'none':
                    nr_sa_included.update(bands_config['nr5g_sa_bands'].get('include', set()))
            if 'nr5g_nsa_bands' in bands_config:
                if bands_config['nr5g_nsa_bands'].get('base') == 'none':
                    nr_nsa_included.update(bands_config['nr5g_nsa_bands'].get('include', set()))

    return CarrierPolicyBands(
        carrier_name=carrier_name,
        policy_version=policy_version,
        gw_excluded=gw_excluded,
        lte_excluded=lte_excluded,
        nr_sa_excluded=nr_sa_excluded,
        nr_nsa_excluded=nr_nsa_excluded,
        nr_sa_included=nr_sa_included,
        nr_nsa_included=nr_nsa_included,
        mcc_lists=mcc_lists,
        band_lists=band_lists
    )


def is_band_excluded(band_num: int, excluded_bands: Set[int]) -> bool:
    """Check if a band is excluded by carrier policy"""
    return band_num in excluded_bands


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = parse_carrier_policy_xml(sys.argv[1])
        if result:
            print(f"\n=== Carrier Policy Parser Results ===")
            print(f"Carrier: {result.carrier_name}")
            print(f"Version: {result.policy_version}")
            print(f"\n(Note: All bands converted from 0-indexed to actual band numbers)")

            print(f"\nMCC Lists:")
            for name, mccs in result.mcc_lists.items():
                print(f"  {name}: {' '.join(mccs)}")

            print(f"\nExcluded Bands (converted to 1-indexed):")
            print(f"  GW: {sorted(result.gw_excluded) if result.gw_excluded else 'None'}")
            print(f"  LTE: {sorted(result.lte_excluded) if result.lte_excluded else 'None'}")
            print(f"  NR SA: {sorted(result.nr_sa_excluded) if result.nr_sa_excluded else 'None'}")
            print(f"  NR NSA: {sorted(result.nr_nsa_excluded) if result.nr_nsa_excluded else 'None'}")

            if result.nr_sa_included or result.nr_nsa_included:
                print(f"\nRoaming Included Bands (converted to 1-indexed):")
                print(f"  NR SA: {sorted(result.nr_sa_included) if result.nr_sa_included else 'None'}")
                print(f"  NR NSA: {sorted(result.nr_nsa_included) if result.nr_nsa_included else 'None'}")

            print(f"\nBand Lists Found: {list(result.band_lists.keys())}")
    else:
        print("Usage: python carrier_policy_parser.py <carrier_policy.xml>")
