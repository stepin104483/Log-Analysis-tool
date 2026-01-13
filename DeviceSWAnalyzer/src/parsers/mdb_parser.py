"""
MDB (Mobile Database) Parser
Parses mcc2bands.xml to extract allowed bands per MCC (country code).

Note: MDB uses 0-indexed bands for ALL band types:
      - LTE: 0=B1, 1=B2, 6=B7, etc.
      - NR NSA: 0=n1, 1=n2, 77=n78, etc.
      - NR SA: 0=n1, 1=n2, 77=n78, etc.
      All band numbers are converted to 1-indexed (actual band numbers) during parsing.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Set, Optional, List
from dataclasses import dataclass


@dataclass
class MDBBands:
    """Container for bands extracted from MDB"""
    mcc_list: List[str]           # MCCs this entry applies to
    lte_bands: Set[int]           # LTE bands (converted to 1-indexed)
    nr_nsa_bands: Set[int]        # NR NSA bands
    nr_sa_bands: Set[int]         # NR SA bands
    cdma_bands: str               # CDMA config ('all' or specific)
    gsm_bands: str                # GSM config
    tds_bands: str                # TD-SCDMA config
    is_default: bool              # True if this is the default (*) entry
    raw_values: Dict[str, str]    # Raw tag values from XML


def parse_band_list(text: str) -> Set[int]:
    """
    Parse space-separated band numbers from MDB.

    Args:
        text: Space-separated numbers like "1 3 4 6 11 12"

    Returns:
        Set of band numbers
    """
    result: Set[int] = set()
    if not text or text.strip().lower() == 'all':
        return result

    for part in text.strip().split():
        try:
            result.add(int(part.strip()))
        except ValueError:
            continue

    return result


def convert_0indexed_to_bands(indices: Set[int]) -> Set[int]:
    """
    Convert 0-indexed band positions to actual band numbers.
    MDB uses 0-indexed for ALL band types: 0=Band 1, 1=Band 2, etc.

    Args:
        indices: Set of 0-indexed positions from MDB

    Returns:
        Set of actual band numbers (1-indexed)
    """
    return {idx + 1 for idx in indices}


# Alias for backward compatibility
convert_lte_0indexed_to_bands = convert_0indexed_to_bands


def parse_mcc2bands_xml(file_path: str, target_mcc: Optional[str] = None) -> Optional[MDBBands]:
    """
    Parse mcc2bands.xml file and optionally filter for a specific MCC.

    Args:
        file_path: Path to mcc2bands.xml
        target_mcc: Specific MCC to look up (e.g., "310"). If None, returns default entry.

    Returns:
        MDBBands object for the matching MCC, or None if parsing fails
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse MDB XML: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] MDB file not found: {file_path}")
        return None

    default_entry = None
    matching_entry = None

    for entry in root.iter('entry'):
        mccs_attr = entry.get('mccs', '')
        mcc_list = mccs_attr.strip().split()

        # Check if this is the default entry
        is_default = '*' in mcc_list

        # Extract band tags
        raw_values: Dict[str, str] = {}

        c_elem = entry.find('c')  # CDMA
        g_elem = entry.find('g')  # GSM
        t_elem = entry.find('t')  # TD-SCDMA
        l_elem = entry.find('l')  # LTE
        n_elem = entry.find('n')  # NR NSA
        s_elem = entry.find('s')  # NR SA

        raw_values['c'] = c_elem.text.strip() if c_elem is not None and c_elem.text else ''
        raw_values['g'] = g_elem.text.strip() if g_elem is not None and g_elem.text else ''
        raw_values['t'] = t_elem.text.strip() if t_elem is not None and t_elem.text else ''
        raw_values['l'] = l_elem.text.strip() if l_elem is not None and l_elem.text else ''
        raw_values['n'] = n_elem.text.strip() if n_elem is not None and n_elem.text else ''
        raw_values['s'] = s_elem.text.strip() if s_elem is not None and s_elem.text else ''

        # Parse band values (raw 0-indexed)
        lte_indices = parse_band_list(raw_values['l'])
        nr_nsa_indices = parse_band_list(raw_values['n'])
        nr_sa_indices = parse_band_list(raw_values['s'])

        # Convert ALL band types from 0-indexed to 1-indexed
        lte_bands = convert_0indexed_to_bands(lte_indices)
        nr_nsa_bands = convert_0indexed_to_bands(nr_nsa_indices)
        nr_sa_bands = convert_0indexed_to_bands(nr_sa_indices)

        # Handle 'all' keyword
        lte_all = raw_values['l'].strip().lower() == 'all'
        nr_nsa_all = raw_values['n'].strip().lower() == 'all'
        nr_sa_all = raw_values['s'].strip().lower() == 'all'

        mdb_bands = MDBBands(
            mcc_list=mcc_list,
            lte_bands=lte_bands if not lte_all else set(),
            nr_nsa_bands=nr_nsa_bands if not nr_nsa_all else set(),
            nr_sa_bands=nr_sa_bands if not nr_sa_all else set(),
            cdma_bands=raw_values['c'],
            gsm_bands=raw_values['g'],
            tds_bands=raw_values['t'],
            is_default=is_default,
            raw_values=raw_values
        )

        # Store default entry
        if is_default:
            default_entry = mdb_bands

        # Check for target MCC match
        if target_mcc and target_mcc in mcc_list:
            matching_entry = mdb_bands

    # Return matching entry or default
    if matching_entry:
        return matching_entry
    return default_entry


def get_all_mcc_entries(file_path: str) -> List[MDBBands]:
    """
    Parse mcc2bands.xml and return all entries.

    Args:
        file_path: Path to mcc2bands.xml

    Returns:
        List of MDBBands objects for all entries
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"[ERROR] Failed to parse MDB XML: {e}")
        return []

    entries = []

    for entry in root.iter('entry'):
        mccs_attr = entry.get('mccs', '')
        mcc_list = mccs_attr.strip().split()
        is_default = '*' in mcc_list

        raw_values: Dict[str, str] = {}
        for tag in ['c', 'g', 't', 'l', 'n', 's']:
            elem = entry.find(tag)
            raw_values[tag] = elem.text.strip() if elem is not None and elem.text else ''

        lte_indices = parse_band_list(raw_values['l'])
        nr_nsa_indices = parse_band_list(raw_values['n'])
        nr_sa_indices = parse_band_list(raw_values['s'])

        # Convert ALL band types from 0-indexed to 1-indexed
        lte_bands = convert_0indexed_to_bands(lte_indices) if raw_values['l'].lower() != 'all' else set()
        nr_nsa_bands = convert_0indexed_to_bands(nr_nsa_indices) if raw_values['n'].lower() != 'all' else set()
        nr_sa_bands = convert_0indexed_to_bands(nr_sa_indices) if raw_values['s'].lower() != 'all' else set()

        entries.append(MDBBands(
            mcc_list=mcc_list,
            lte_bands=lte_bands,
            nr_nsa_bands=nr_nsa_bands,
            nr_sa_bands=nr_sa_bands,
            cdma_bands=raw_values['c'],
            gsm_bands=raw_values['g'],
            tds_bands=raw_values['t'],
            is_default=is_default,
            raw_values=raw_values
        ))

    return entries


def is_band_allowed_by_mdb(band_num: int, allowed_bands: Set[int], is_all: bool = False) -> bool:
    """
    Check if a band is allowed by MDB.

    Args:
        band_num: Band number to check
        allowed_bands: Set of allowed bands (empty if 'all')
        is_all: True if the MDB config says 'all'

    Returns:
        True if band is allowed
    """
    if is_all:
        return True
    return band_num in allowed_bands


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        target_mcc = sys.argv[2] if len(sys.argv) > 2 else None

        result = parse_mcc2bands_xml(file_path, target_mcc)
        if result:
            print(f"\n=== MDB Parser Results ===")
            print(f"MCCs: {' '.join(result.mcc_list)}")
            print(f"Is Default Entry: {result.is_default}")

            print(f"\nRaw Values (0-indexed):")
            for key, value in result.raw_values.items():
                print(f"  <{key}>: {value if value else '(empty)'}")

            print(f"\nParsed Bands (ALL converted from 0-indexed to 1-indexed):")
            if result.raw_values['l'].lower() == 'all':
                print(f"  LTE: ALL")
            else:
                print(f"  LTE: {sorted(result.lte_bands) if result.lte_bands else 'None'}")

            if result.raw_values['n'].lower() == 'all':
                print(f"  NR NSA: ALL")
            else:
                print(f"  NR NSA: {sorted(result.nr_nsa_bands) if result.nr_nsa_bands else 'None'}")

            if result.raw_values['s'].lower() == 'all':
                print(f"  NR SA: ALL")
            else:
                print(f"  NR SA: {sorted(result.nr_sa_bands) if result.nr_sa_bands else 'None'}")
    else:
        print("Usage: python mdb_parser.py <mcc2bands.xml> [target_mcc]")
        print("Example: python mdb_parser.py mcc2bands.xml 310")
