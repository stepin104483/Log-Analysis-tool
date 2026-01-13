"""
MCFG NV Band Preference Parser
Parses MCFG XML files to extract NV band preference bitmasks.

NV Items parsed:
- NV 65633 (lte_bandpref): LTE bands 1-64
- NV 73680 (lte_bandpref_ext): LTE bands 65-256
- NV 74087 (nr5g_sa_bandpref): NR SA bands
- NV 74213 (nr5g_nsa_bandpref): NR NSA bands

Note: Bit 0 = Band 1 (1-indexed mapping)
"""

import xml.etree.ElementTree as ET
from typing import Dict, Set, Optional, List
from dataclasses import dataclass


# NV Item IDs for band preferences
NV_LTE_BANDPREF = 65633       # LTE bands 1-64
NV_LTE_BANDPREF_EXT = 73680   # LTE bands 65-256
NV_NR5G_SA_BANDPREF = 74087   # NR SA bands
NV_NR5G_NSA_BANDPREF = 74213  # NR NSA bands


@dataclass
class MCFGBandPrefs:
    """Container for band preferences extracted from MCFG NV items"""
    lte_bands: Set[int]       # LTE bands 1-64 from NV 65633
    lte_ext_bands: Set[int]   # LTE bands 65+ from NV 73680
    nr_sa_bands: Set[int]     # NR SA bands from NV 74087
    nr_nsa_bands: Set[int]    # NR NSA bands from NV 74213
    raw_nv_data: Dict[int, List[int]]  # Raw NV ID -> byte values
    nv_present: Dict[int, bool]  # Which NV items were found


def parse_nv_bytes(byte_string: str) -> List[int]:
    """
    Parse space-separated byte values from NV Member text.

    Args:
        byte_string: Space-separated decimal byte values (e.g., "223 56 14 187 224 135 0 0")

    Returns:
        List of integer byte values
    """
    if not byte_string or not byte_string.strip():
        return []

    try:
        return [int(b) for b in byte_string.strip().split()]
    except ValueError as e:
        print(f"[WARNING] Failed to parse NV bytes: {e}")
        return []


def decode_band_bitmask(nv_bytes: List[int], start_band: int = 1) -> Set[int]:
    """
    Decode NV band preference bitmask to extract enabled bands.

    Each byte contains 8 bits, each bit representing a band's enable status.
    Bit 0 of byte 0 = Band (start_band)
    Bit 7 of byte 0 = Band (start_band + 7)
    Bit 0 of byte 1 = Band (start_band + 8)
    etc.

    Args:
        nv_bytes: List of byte values from NV item
        start_band: Starting band number (1 for NV65633, 65 for NV73680)

    Returns:
        Set of enabled band numbers (1-indexed)
    """
    enabled_bands: Set[int] = set()

    for byte_idx, byte_val in enumerate(nv_bytes):
        for bit_pos in range(8):
            if byte_val & (1 << bit_pos):  # Check if bit is set
                band_num = start_band + (byte_idx * 8) + bit_pos
                enabled_bands.add(band_num)

    return enabled_bands


def parse_mcfg_xml(file_path: str) -> Optional[MCFGBandPrefs]:
    """
    Parse MCFG XML file to extract NV band preferences.

    Args:
        file_path: Path to MCFG XML file (e.g., mcfg_sw_gen_VoLTE.xml)

    Returns:
        MCFGBandPrefs object, or None if parsing fails
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse MCFG XML: {e}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] MCFG file not found: {file_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read MCFG file: {e}")
        return None

    raw_nv_data: Dict[int, List[int]] = {}
    nv_present: Dict[int, bool] = {
        NV_LTE_BANDPREF: False,
        NV_LTE_BANDPREF_EXT: False,
        NV_NR5G_SA_BANDPREF: False,
        NV_NR5G_NSA_BANDPREF: False
    }

    # Find all NV items (both NvItemData and NvEfsItemData)
    for tag in ['NvItemData', 'NvEfsItemData']:
        for nv_item in root.findall(f'.//{tag}'):
            try:
                nv_id = int(nv_item.get('id', 0))
            except (ValueError, TypeError):
                continue

            # Check if this is a band preference NV item we care about
            if nv_id not in [NV_LTE_BANDPREF, NV_LTE_BANDPREF_EXT,
                            NV_NR5G_SA_BANDPREF, NV_NR5G_NSA_BANDPREF]:
                continue

            # Extract the Member value
            member = nv_item.find('Member')
            if member is not None and member.text:
                nv_bytes = parse_nv_bytes(member.text)
                if nv_bytes:
                    raw_nv_data[nv_id] = nv_bytes
                    nv_present[nv_id] = True

    # Decode band bitmasks
    lte_bands: Set[int] = set()
    lte_ext_bands: Set[int] = set()
    nr_sa_bands: Set[int] = set()
    nr_nsa_bands: Set[int] = set()

    if NV_LTE_BANDPREF in raw_nv_data:
        lte_bands = decode_band_bitmask(raw_nv_data[NV_LTE_BANDPREF], start_band=1)

    if NV_LTE_BANDPREF_EXT in raw_nv_data:
        lte_ext_bands = decode_band_bitmask(raw_nv_data[NV_LTE_BANDPREF_EXT], start_band=65)

    if NV_NR5G_SA_BANDPREF in raw_nv_data:
        nr_sa_bands = decode_band_bitmask(raw_nv_data[NV_NR5G_SA_BANDPREF], start_band=1)

    if NV_NR5G_NSA_BANDPREF in raw_nv_data:
        nr_nsa_bands = decode_band_bitmask(raw_nv_data[NV_NR5G_NSA_BANDPREF], start_band=1)

    return MCFGBandPrefs(
        lte_bands=lte_bands,
        lte_ext_bands=lte_ext_bands,
        nr_sa_bands=nr_sa_bands,
        nr_nsa_bands=nr_nsa_bands,
        raw_nv_data=raw_nv_data,
        nv_present=nv_present
    )


def get_all_lte_bands(mcfg: MCFGBandPrefs) -> Set[int]:
    """
    Get combined LTE bands from both NV 65633 and NV 73680.

    Args:
        mcfg: MCFGBandPrefs object

    Returns:
        Combined set of all enabled LTE bands
    """
    return mcfg.lte_bands | mcfg.lte_ext_bands


def is_band_enabled_in_nv(band_num: int, enabled_bands: Set[int], nv_present: bool) -> Optional[bool]:
    """
    Check if a band is enabled in NV band preference.

    Args:
        band_num: Band number to check (1-indexed)
        enabled_bands: Set of enabled band numbers from NV
        nv_present: Whether the NV item was present in MCFG

    Returns:
        True if enabled, False if disabled, None if NV not present (skip check)
    """
    if not nv_present:
        return None  # NV not present, cannot determine - skip this check
    return band_num in enabled_bands


def format_bands_display(bands: Set[int], prefix: str = '', max_display: int = 30) -> str:
    """Format band set for display"""
    if not bands:
        return "None"
    sorted_bands = sorted(bands)
    if len(sorted_bands) > max_display:
        displayed = sorted_bands[:max_display]
        return f"{', '.join(f'{prefix}{b}' for b in displayed)}... ({len(sorted_bands)} total)"
    return ', '.join(f'{prefix}{b}' for b in sorted_bands)


def format_bytes_hex(nv_bytes: List[int]) -> str:
    """Format byte list as hex string"""
    return ' '.join(f'{b:02X}' for b in nv_bytes)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = parse_mcfg_xml(sys.argv[1])
        if result:
            print(f"\n=== MCFG NV Band Preference Parser Results ===")

            print(f"\nNV Items Found:")
            print(f"  NV 65633 (LTE B1-64):   {'Present' if result.nv_present[NV_LTE_BANDPREF] else 'NOT FOUND'}")
            print(f"  NV 73680 (LTE B65-256): {'Present' if result.nv_present[NV_LTE_BANDPREF_EXT] else 'NOT FOUND'}")
            print(f"  NV 74087 (NR SA):       {'Present' if result.nv_present[NV_NR5G_SA_BANDPREF] else 'NOT FOUND'}")
            print(f"  NV 74213 (NR NSA):      {'Present' if result.nv_present[NV_NR5G_NSA_BANDPREF] else 'NOT FOUND'}")

            print(f"\nRaw NV Data:")
            for nv_id, nv_bytes in result.raw_nv_data.items():
                print(f"  NV {nv_id}: {' '.join(map(str, nv_bytes))}")
                print(f"           Hex: {format_bytes_hex(nv_bytes)}")

            print(f"\nEnabled Bands (decoded from bitmasks):")
            print(f"  LTE B1-64 ({len(result.lte_bands)}):  {format_bands_display(result.lte_bands, 'B')}")
            if result.lte_ext_bands:
                print(f"  LTE B65+ ({len(result.lte_ext_bands)}): {format_bands_display(result.lte_ext_bands, 'B')}")
            if result.nr_sa_bands:
                print(f"  NR SA ({len(result.nr_sa_bands)}):    {format_bands_display(result.nr_sa_bands, 'n')}")
            if result.nr_nsa_bands:
                print(f"  NR NSA ({len(result.nr_nsa_bands)}):   {format_bands_display(result.nr_nsa_bands, 'n')}")

            # Show combined LTE bands
            all_lte = get_all_lte_bands(result)
            print(f"\n  Combined LTE ({len(all_lte)}): {format_bands_display(all_lte, 'B')}")

            # Show which common bands are DISABLED
            if result.nv_present[NV_LTE_BANDPREF]:
                common_lte = {1, 2, 3, 4, 5, 7, 8, 12, 13, 14, 17, 20, 25, 26, 28, 29, 30, 38, 39, 40, 41, 42, 43, 46, 48, 66}
                disabled_lte = common_lte - result.lte_bands
                if disabled_lte:
                    print(f"\n  DISABLED LTE bands (common): {format_bands_display(disabled_lte, 'B')}")
        else:
            print("[ERROR] Failed to parse MCFG XML")
    else:
        print("Usage: python mcfg_parser.py <mcfg_xml_file>")
        print("\nExample: python mcfg_parser.py mcfg_sw_gen_VoLTE.xml")
        print("\nParses NV band preference items:")
        print("  - NV 65633: LTE bands 1-64")
        print("  - NV 73680: LTE bands 65-256")
        print("  - NV 74087: NR SA bands")
        print("  - NV 74213: NR NSA bands")
