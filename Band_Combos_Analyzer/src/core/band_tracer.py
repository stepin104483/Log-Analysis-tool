"""
Band Tracer Engine
Traces each band through all filtering stages to determine PASS/FAIL status.
"""

from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class BandStatus(Enum):
    """Status of a band at each stage"""
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "N/A"        # Stage not applicable (document not provided)
    SKIPPED = "SKIP"  # Stage skipped (band already filtered)


class FinalStatus(Enum):
    """Final status of a band after all stages"""
    ENABLED = "ENABLED"           # Passes all stages
    FILTERED = "FILTERED"         # Filtered at some stage
    MISSING_IN_PM = "MISSING_IN_PM"  # In config but not in QXDM
    MISSING_IN_UE = "MISSING_IN_UE"  # In QXDM but not in UE Cap
    NOT_SUPPORTED = "NOT_SUPPORTED"  # Not in RFC (hardware)
    ANOMALY = "ANOMALY"           # Unexpected behavior


@dataclass
class BandTraceResult:
    """Result of tracing a single band through all stages"""
    band_num: int
    band_type: str  # 'LTE', 'NR_SA', 'NR_NSA'
    stages: Dict[str, BandStatus] = field(default_factory=dict)
    final_status: FinalStatus = FinalStatus.ENABLED
    filtered_at: Optional[str] = None
    anomaly_reason: Optional[str] = None


@dataclass
class DocumentStatus:
    """Status of each input document"""
    name: str
    loaded: bool
    band_count: Optional[int] = None
    details: str = ""


class BandTracer:
    """
    Traces bands through filtering pipeline.

    Filtering Stages:
    1. RFC - RF Card supported bands
    2. HW Filter - Hardware band filtering
    3. Carrier - Carrier policy exclusions
    4. Generic - FCC/regulatory restrictions
    5. NV_Pref - MCFG NV band preferences (SW level filtering)
    6. QXDM - Actual device bands (0x1CCA)
    7. UE Cap - Network-reported bands

    Note: MDB is NOT a filtering stage. MDB data is stored for Claude context only.

    Supported RAT Types:
    - GSM (2G): Bands identified by frequency - 850, 900, 1800, 1900 MHz
    - WCDMA (3G): Bands 1-26 (numbered like LTE)
    - LTE (4G): Bands 1-256+
    - NR SA (5G Standalone): Bands n1-n512
    - NR NSA (5G Non-Standalone): Bands n1-n512
    """

    STAGES = ['RFC', 'HW_Filter', 'Carrier', 'Generic', 'NV_Pref', 'QXDM', 'UE_Cap']

    # Standard GSM frequency bands
    GSM_BANDS = ['850', '900', '1800', '1900']

    # WCDMA bands typically range from 1-26
    WCDMA_MAX_BAND = 26

    def __init__(self):
        # GSM (2G) bands - stored as frequency strings
        self.rfc_gsm: Set[str] = set()
        self.hw_gw: Set[int] = set()  # Combined GSM/WCDMA mask (0-indexed converted to bands)
        self.carrier_gw_excluded: Set[int] = set()

        # WCDMA (3G) bands - stored as integers (band 1-26)
        self.rfc_wcdma: Set[int] = set()

        # LTE (4G) bands
        self.rfc_lte: Set[int] = set()
        self.rfc_nr: Set[int] = set()

        self.hw_lte: Set[int] = set()
        self.hw_nr_sa: Set[int] = set()
        self.hw_nr_nsa: Set[int] = set()

        self.carrier_lte_excluded: Set[int] = set()
        self.carrier_nr_sa_excluded: Set[int] = set()
        self.carrier_nr_nsa_excluded: Set[int] = set()

        self.generic_lte_excluded: Set[int] = set()
        self.generic_nr_excluded: Set[int] = set()

        # NV Band Preferences (enabled bands from MCFG NV items)
        self.nv_lte: Set[int] = set()          # LTE enabled bands from NV 65633 + 73680
        self.nv_nr_sa: Set[int] = set()        # NR SA enabled bands from NV 74087
        self.nv_nr_nsa: Set[int] = set()       # NR NSA enabled bands from NV 74213
        self.nv_lte_base_present: bool = False   # Is NV 65633 (B1-64) present?
        self.nv_lte_ext_present: bool = False    # Is NV 73680 (B65+) present?
        self.nv_nr_sa_present: bool = False    # Is NV 74087 present?
        self.nv_nr_nsa_present: bool = False   # Is NV 74213 present?

        self.mdb_lte: Set[int] = set()
        self.mdb_nr_sa: Set[int] = set()
        self.mdb_nr_nsa: Set[int] = set()
        self.mdb_lte_all: bool = False
        self.mdb_nr_sa_all: bool = False
        self.mdb_nr_nsa_all: bool = False

        self.qxdm_lte: Set[int] = set()
        self.qxdm_nr_sa: Set[int] = set()
        self.qxdm_nr_nsa: Set[int] = set()

        self.ue_cap_lte: Set[int] = set()
        self.ue_cap_nr: Set[int] = set()           # General NR bands (rf-Parameters)
        self.ue_cap_nr_sa: Set[int] = set()        # NR SA bands (supportedBandListNR-SA-r15)
        self.ue_cap_nr_nsa: Set[int] = set()       # NR NSA bands (supportedBandListEN-DC-r15)

        # Document status
        self.doc_status: Dict[str, DocumentStatus] = {
            'RFC': DocumentStatus('RFC XML', False),
            'HW_Filter': DocumentStatus('HW Band Filtering', False),
            'Carrier': DocumentStatus('Carrier Policy', False),
            'Generic': DocumentStatus('Generic Restrictions', False),
            'NV_Pref': DocumentStatus('MCFG NV Band Pref', False),  # NV band preferences
            'MDB': DocumentStatus('MDB Config (Context)', False),  # Context only, not filtering
            'QXDM': DocumentStatus('QXDM Log', False),
            'UE_Cap': DocumentStatus('UE Capability', False),
        }

    def set_rfc_bands(self, lte_bands: Set[int], nr_bands: Set[int],
                      gsm_bands: Optional[Set[str]] = None):
        """Set RFC bands including optional GSM bands"""
        self.rfc_lte = lte_bands
        self.rfc_nr = nr_bands
        if gsm_bands:
            # Normalize GSM band names (strip 'B' prefix if present)
            self.rfc_gsm = {b.replace('B', '').replace('b', '') for b in gsm_bands}
        self.doc_status['RFC'].loaded = True
        self.doc_status['RFC'].band_count = len(lte_bands) + len(nr_bands)
        details = f"{len(lte_bands)} LTE, {len(nr_bands)} NR"
        if gsm_bands:
            details += f", {len(gsm_bands)} GSM"
        self.doc_status['RFC'].details = details

    def set_hw_filter_bands(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int],
                            gw: Optional[Set[int]] = None):
        """Set HW filter allowed bands including optional GW (GSM/WCDMA) bands"""
        self.hw_lte = lte
        self.hw_nr_sa = nr_sa
        self.hw_nr_nsa = nr_nsa
        if gw is not None:
            self.hw_gw = gw
        self.doc_status['HW_Filter'].loaded = True
        self.doc_status['HW_Filter'].details = "Loaded"

    def set_carrier_exclusions(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int],
                               gw: Optional[Set[int]] = None):
        """Set carrier policy excluded bands including optional GW (GSM/WCDMA)"""
        self.carrier_lte_excluded = lte
        self.carrier_nr_sa_excluded = nr_sa
        self.carrier_nr_nsa_excluded = nr_nsa
        if gw is not None:
            self.carrier_gw_excluded = gw
        self.doc_status['Carrier'].loaded = True
        details = f"Excl: {len(lte)} LTE, {len(nr_sa)} NR"
        if gw:
            details += f", {len(gw)} GW"
        self.doc_status['Carrier'].details = details

    def set_generic_exclusions(self, lte: Set[int], nr: Set[int]):
        """Set generic restriction excluded bands"""
        self.generic_lte_excluded = lte
        self.generic_nr_excluded = nr
        self.doc_status['Generic'].loaded = True
        self.doc_status['Generic'].details = f"Excl: {len(lte)} LTE, {len(nr)} NR"

    def set_nv_band_prefs(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int],
                         lte_base_present: bool = False, lte_ext_present: bool = False,
                         nr_sa_present: bool = False, nr_nsa_present: bool = False):
        """
        Set NV band preferences (enabled bands from MCFG NV items).

        Args:
            lte: Set of enabled LTE bands from NV 65633 + NV 73680
            nr_sa: Set of enabled NR SA bands from NV 74087
            nr_nsa: Set of enabled NR NSA bands from NV 74213
            lte_base_present: Whether NV 65633 (B1-64) was found
            lte_ext_present: Whether NV 73680 (B65+) was found
            nr_sa_present: Whether NR SA NV item was found
            nr_nsa_present: Whether NR NSA NV item was found
        """
        self.nv_lte = lte
        self.nv_nr_sa = nr_sa
        self.nv_nr_nsa = nr_nsa
        self.nv_lte_base_present = lte_base_present
        self.nv_lte_ext_present = lte_ext_present
        self.nv_nr_sa_present = nr_sa_present
        self.nv_nr_nsa_present = nr_nsa_present
        self.doc_status['NV_Pref'].loaded = True

        # Build details string
        details_parts = []
        if lte_base_present or lte_ext_present:
            details_parts.append(f"{len(lte)} LTE")
        if nr_sa_present:
            details_parts.append(f"{len(nr_sa)} NR SA")
        if nr_nsa_present:
            details_parts.append(f"{len(nr_nsa)} NR NSA")

        if details_parts:
            self.doc_status['NV_Pref'].details = "Enabled: " + ", ".join(details_parts)
        else:
            self.doc_status['NV_Pref'].details = "No band pref NVs found"

    def set_mdb_bands(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int],
                      lte_all: bool = False, nr_sa_all: bool = False, nr_nsa_all: bool = False):
        """Set MDB allowed bands (for Claude context only, NOT used in filtering)"""
        self.mdb_lte = lte
        self.mdb_nr_sa = nr_sa
        self.mdb_nr_nsa = nr_nsa
        self.mdb_lte_all = lte_all
        self.mdb_nr_sa_all = nr_sa_all
        self.mdb_nr_nsa_all = nr_nsa_all
        self.doc_status['MDB'].loaded = True
        self.doc_status['MDB'].details = f"Context: {len(lte)} LTE, {len(nr_sa)} NR"

    def set_qxdm_bands(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int]):
        """Set QXDM 0x1CCA bands"""
        self.qxdm_lte = lte
        self.qxdm_nr_sa = nr_sa
        self.qxdm_nr_nsa = nr_nsa
        self.doc_status['QXDM'].loaded = True
        self.doc_status['QXDM'].band_count = len(lte) + len(nr_sa)
        self.doc_status['QXDM'].details = f"{len(lte)} LTE, {len(nr_sa)} NR SA"

    def set_ue_cap_bands(self, lte: Set[int], nr: Set[int],
                         nr_sa: Optional[Set[int]] = None, nr_nsa: Optional[Set[int]] = None):
        """
        Set UE Capability bands.

        Args:
            lte: LTE bands from UE Capability
            nr: General NR bands (from rf-Parameters.supportedBandListNR)
            nr_sa: NR SA bands (from supportedBandListNR-SA-r15)
            nr_nsa: NR NSA bands (from supportedBandListEN-DC-r15)
        """
        self.ue_cap_lte = lte
        self.ue_cap_nr = nr
        self.ue_cap_nr_sa = nr_sa if nr_sa is not None else set()
        self.ue_cap_nr_nsa = nr_nsa if nr_nsa is not None else set()
        self.doc_status['UE_Cap'].loaded = True
        self.doc_status['UE_Cap'].band_count = len(lte) + len(nr)

        # Build details string
        details = f"{len(lte)} LTE"
        if nr_sa:
            details += f", {len(nr_sa)} NR SA"
        if nr_nsa:
            details += f", {len(nr_nsa)} NR NSA"
        if not nr_sa and not nr_nsa and nr:
            details += f", {len(nr)} NR"
        self.doc_status['UE_Cap'].details = details

    def trace_lte_band(self, band: int) -> BandTraceResult:
        """Trace a single LTE band through all stages"""
        result = BandTraceResult(band_num=band, band_type='LTE')
        filtered = False

        # Stage 1: RFC
        if self.doc_status['RFC'].loaded:
            if band in self.rfc_lte:
                result.stages['RFC'] = BandStatus.PASS
            else:
                result.stages['RFC'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'RFC'
        else:
            result.stages['RFC'] = BandStatus.NA

        # Stage 2: HW Filter
        if filtered:
            result.stages['HW_Filter'] = BandStatus.SKIPPED
        elif not self.doc_status['HW_Filter'].loaded:
            result.stages['HW_Filter'] = BandStatus.NA
        else:
            if band in self.hw_lte:
                result.stages['HW_Filter'] = BandStatus.PASS
            else:
                result.stages['HW_Filter'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'HW_Filter'

        # Stage 3: Carrier Policy
        if filtered:
            result.stages['Carrier'] = BandStatus.SKIPPED
        elif not self.doc_status['Carrier'].loaded:
            result.stages['Carrier'] = BandStatus.NA
        else:
            if band in self.carrier_lte_excluded:
                result.stages['Carrier'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'Carrier'
            else:
                result.stages['Carrier'] = BandStatus.PASS

        # Stage 4: Generic Restrictions
        if filtered:
            result.stages['Generic'] = BandStatus.SKIPPED
        elif not self.doc_status['Generic'].loaded:
            result.stages['Generic'] = BandStatus.NA
        else:
            if band in self.generic_lte_excluded:
                result.stages['Generic'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'Generic'
            else:
                result.stages['Generic'] = BandStatus.PASS

        # Stage 5: NV Band Preference (MCFG NV items)
        # NV 65633 covers B1-64, NV 73680 covers B65+
        # Only check NV if the corresponding NV item for this band range is present
        if filtered:
            result.stages['NV_Pref'] = BandStatus.SKIPPED
        elif not self.doc_status['NV_Pref'].loaded:
            result.stages['NV_Pref'] = BandStatus.NA
        else:
            # Determine which NV item should cover this band
            if band <= 64:
                nv_applicable = self.nv_lte_base_present
            else:
                nv_applicable = self.nv_lte_ext_present

            if not nv_applicable:
                # NV for this band range not present - skip check
                result.stages['NV_Pref'] = BandStatus.NA
            elif band in self.nv_lte:
                result.stages['NV_Pref'] = BandStatus.PASS
            else:
                result.stages['NV_Pref'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'NV_Pref'

        # Note: MDB is NOT a filtering stage - data stored for Claude context only

        # Stage 6: QXDM
        if not self.doc_status['QXDM'].loaded:
            result.stages['QXDM'] = BandStatus.NA
        else:
            if band in self.qxdm_lte:
                result.stages['QXDM'] = BandStatus.PASS
            else:
                result.stages['QXDM'] = BandStatus.FAIL

        # Stage 7: UE Capability
        if not self.doc_status['UE_Cap'].loaded:
            result.stages['UE_Cap'] = BandStatus.NA
        else:
            if band in self.ue_cap_lte:
                result.stages['UE_Cap'] = BandStatus.PASS
            else:
                result.stages['UE_Cap'] = BandStatus.FAIL

        # Determine final status
        result.final_status = self._determine_final_status(result, filtered)

        return result

    def trace_nr_band(self, band: int, mode: str = 'SA') -> BandTraceResult:
        """Trace a single NR band through all stages"""
        result = BandTraceResult(band_num=band, band_type=f'NR_{mode}')
        filtered = False

        # Select appropriate band sets based on mode
        hw_bands = self.hw_nr_sa if mode == 'SA' else self.hw_nr_nsa
        carrier_excluded = self.carrier_nr_sa_excluded if mode == 'SA' else self.carrier_nr_nsa_excluded
        qxdm_bands = self.qxdm_nr_sa if mode == 'SA' else self.qxdm_nr_nsa
        nv_bands = self.nv_nr_sa if mode == 'SA' else self.nv_nr_nsa
        nv_present = self.nv_nr_sa_present if mode == 'SA' else self.nv_nr_nsa_present

        # Stage 1: RFC
        if self.doc_status['RFC'].loaded:
            if band in self.rfc_nr:
                result.stages['RFC'] = BandStatus.PASS
            else:
                result.stages['RFC'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'RFC'
        else:
            result.stages['RFC'] = BandStatus.NA

        # Stage 2: HW Filter
        if filtered:
            result.stages['HW_Filter'] = BandStatus.SKIPPED
        elif not self.doc_status['HW_Filter'].loaded:
            result.stages['HW_Filter'] = BandStatus.NA
        else:
            if band in hw_bands:
                result.stages['HW_Filter'] = BandStatus.PASS
            else:
                result.stages['HW_Filter'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'HW_Filter'

        # Stage 3: Carrier Policy
        if filtered:
            result.stages['Carrier'] = BandStatus.SKIPPED
        elif not self.doc_status['Carrier'].loaded:
            result.stages['Carrier'] = BandStatus.NA
        else:
            if band in carrier_excluded:
                result.stages['Carrier'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'Carrier'
            else:
                result.stages['Carrier'] = BandStatus.PASS

        # Stage 4: Generic Restrictions
        if filtered:
            result.stages['Generic'] = BandStatus.SKIPPED
        elif not self.doc_status['Generic'].loaded:
            result.stages['Generic'] = BandStatus.NA
        else:
            if band in self.generic_nr_excluded:
                result.stages['Generic'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'Generic'
            else:
                result.stages['Generic'] = BandStatus.PASS

        # Stage 5: NV Band Preference (MCFG NV items)
        if filtered:
            result.stages['NV_Pref'] = BandStatus.SKIPPED
        elif not self.doc_status['NV_Pref'].loaded or not nv_present:
            # NV item not present - skip this check (band passes by default)
            result.stages['NV_Pref'] = BandStatus.NA
        else:
            if band in nv_bands:
                result.stages['NV_Pref'] = BandStatus.PASS
            else:
                result.stages['NV_Pref'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'NV_Pref'

        # Note: MDB is NOT a filtering stage - data stored for Claude context only

        # Stage 6: QXDM
        if not self.doc_status['QXDM'].loaded:
            result.stages['QXDM'] = BandStatus.NA
        else:
            if band in qxdm_bands:
                result.stages['QXDM'] = BandStatus.PASS
            else:
                result.stages['QXDM'] = BandStatus.FAIL

        # Stage 7: UE Capability
        # Use mode-specific UE capability bands (SA vs NSA/ENDC)
        ue_cap_bands = self.ue_cap_nr_sa if mode == 'SA' else self.ue_cap_nr_nsa

        if not self.doc_status['UE_Cap'].loaded:
            result.stages['UE_Cap'] = BandStatus.NA
        elif not ue_cap_bands:
            # No SA/NSA specific bands in UE Capability - mark as N/A
            result.stages['UE_Cap'] = BandStatus.NA
        else:
            if band in ue_cap_bands:
                result.stages['UE_Cap'] = BandStatus.PASS
            else:
                result.stages['UE_Cap'] = BandStatus.FAIL

        # Determine final status
        result.final_status = self._determine_final_status(result, filtered)

        return result

    def trace_gsm_band(self, band: str) -> BandTraceResult:
        """
        Trace a single GSM band through applicable stages.

        GSM bands are identified by frequency: 850, 900, 1800, 1900 MHz.
        Simplified pipeline since GSM doesn't have all stages like LTE/NR.
        """
        result = BandTraceResult(band_num=int(band), band_type='GSM')
        filtered = False

        # Stage 1: RFC - Check if GSM band is in RFC
        if self.doc_status['RFC'].loaded:
            if band in self.rfc_gsm:
                result.stages['RFC'] = BandStatus.PASS
            else:
                result.stages['RFC'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'RFC'
        else:
            result.stages['RFC'] = BandStatus.NA

        # Stage 2: HW Filter - GSM uses gw_bands mask
        # Note: GSM bands in hw_gw use a different indexing than numbered bands
        # For simplicity, we mark as N/A since GSM indexing is complex
        result.stages['HW_Filter'] = BandStatus.NA

        # Stage 3: Carrier Policy
        # GSM carrier exclusions would be in gw_excluded but use different indexing
        result.stages['Carrier'] = BandStatus.NA

        # Stages 4-7: Not applicable for GSM
        result.stages['Generic'] = BandStatus.NA
        result.stages['NV_Pref'] = BandStatus.NA
        result.stages['QXDM'] = BandStatus.NA
        result.stages['UE_Cap'] = BandStatus.NA

        # Determine final status
        if filtered:
            result.final_status = FinalStatus.FILTERED
        else:
            result.final_status = FinalStatus.ENABLED

        return result

    def trace_wcdma_band(self, band: int) -> BandTraceResult:
        """
        Trace a single WCDMA (3G) band through applicable stages.

        WCDMA bands are numbered 1-26, similar to LTE but for 3G.
        Uses gw_bands mask from HW filter and carrier policy.
        """
        result = BandTraceResult(band_num=band, band_type='WCDMA')
        filtered = False

        # Stage 1: RFC - WCDMA bands would appear similar to LTE bands in RFC
        # RFC doesn't typically distinguish WCDMA from LTE in band naming
        result.stages['RFC'] = BandStatus.NA

        # Stage 2: HW Filter - WCDMA uses gw_bands mask
        if filtered:
            result.stages['HW_Filter'] = BandStatus.SKIPPED
        elif not self.doc_status['HW_Filter'].loaded or not self.hw_gw:
            result.stages['HW_Filter'] = BandStatus.NA
        else:
            # gw_bands is 0-indexed, so band 1 = index 0
            if band in self.hw_gw:
                result.stages['HW_Filter'] = BandStatus.PASS
            else:
                result.stages['HW_Filter'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'HW_Filter'

        # Stage 3: Carrier Policy
        if filtered:
            result.stages['Carrier'] = BandStatus.SKIPPED
        elif not self.doc_status['Carrier'].loaded or not self.carrier_gw_excluded:
            result.stages['Carrier'] = BandStatus.NA
        else:
            if band in self.carrier_gw_excluded:
                result.stages['Carrier'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'Carrier'
            else:
                result.stages['Carrier'] = BandStatus.PASS

        # Stages 4-7: Not typically applicable for WCDMA
        result.stages['Generic'] = BandStatus.NA
        result.stages['NV_Pref'] = BandStatus.NA
        result.stages['QXDM'] = BandStatus.NA
        result.stages['UE_Cap'] = BandStatus.NA

        # Determine final status
        if filtered:
            result.final_status = FinalStatus.FILTERED
        else:
            result.final_status = FinalStatus.ENABLED

        return result

    def _determine_final_status(self, result: BandTraceResult, filtered: bool) -> FinalStatus:
        """Determine final status based on stage results"""

        # Check for anomalies first
        rfc_status = result.stages.get('RFC', BandStatus.NA)
        qxdm_status = result.stages.get('QXDM', BandStatus.NA)
        ue_cap_status = result.stages.get('UE_Cap', BandStatus.NA)

        # Anomaly: Not in RFC but appears in QXDM or UE Cap
        if rfc_status == BandStatus.FAIL:
            if qxdm_status == BandStatus.PASS or ue_cap_status == BandStatus.PASS:
                result.anomaly_reason = "Present in device logs but NOT in RFC"
                return FinalStatus.ANOMALY
            return FinalStatus.NOT_SUPPORTED

        # Band should be enabled - check if it appears in QXDM/UE Cap
        if not filtered:
            if qxdm_status == BandStatus.FAIL and ue_cap_status != BandStatus.NA:
                result.anomaly_reason = "Passed all config stages but missing in QXDM"
                return FinalStatus.MISSING_IN_PM

            if ue_cap_status == BandStatus.FAIL and qxdm_status == BandStatus.PASS:
                result.anomaly_reason = "Present in QXDM but missing in UE Capability"
                return FinalStatus.MISSING_IN_UE

            # All good
            if qxdm_status != BandStatus.FAIL and ue_cap_status != BandStatus.FAIL:
                return FinalStatus.ENABLED

        # Band was filtered
        if filtered:
            return FinalStatus.FILTERED

        return FinalStatus.ENABLED

    def get_all_bands(self) -> Set[int]:
        """
        Get union of all bands from meaningful sources for analysis.

        Includes:
        - RFC bands (hardware supported)
        - Carrier Policy excluded bands (indicates bands that exist)
        - Generic Restriction excluded bands (indicates bands that exist)
        - QXDM bands (actual device bands)
        - UE Capability bands (network-reported)

        Excludes:
        - HW filter ranges (broad whitelist ranges 0-255/0-511)
        - MDB bands (location-dependent, passed to Claude as context only)
        """
        all_lte = (self.rfc_lte | self.qxdm_lte | self.ue_cap_lte |
                   self.carrier_lte_excluded | self.generic_lte_excluded)
        all_nr = (self.rfc_nr | self.qxdm_nr_sa | self.qxdm_nr_nsa |
                  self.ue_cap_nr | self.ue_cap_nr_sa | self.ue_cap_nr_nsa |
                  self.carrier_nr_sa_excluded | self.carrier_nr_nsa_excluded |
                  self.generic_nr_excluded)
        return all_lte, all_nr

    def trace_all_bands(self) -> Dict[str, List[BandTraceResult]]:
        """Trace all bands from all sources including 2G/3G"""
        results = {
            'GSM': [],
            'WCDMA': [],
            'LTE': [],
            'NR_SA': [],
            'NR_NSA': []
        }

        # Get all unique bands
        all_lte, all_nr = self.get_all_bands()

        # Trace GSM bands (from RFC)
        gsm_bands = self.rfc_gsm if self.rfc_gsm else set()
        # Also include all standard GSM bands if RFC is loaded
        if self.doc_status['RFC'].loaded:
            for band in self.GSM_BANDS:
                if band in gsm_bands:
                    results['GSM'].append(self.trace_gsm_band(band))

        # Trace WCDMA bands (bands 1-26 from HW gw_bands mask)
        if self.hw_gw:
            # Only trace WCDMA bands that are in the gw_bands range (1-26)
            wcdma_bands = {b for b in self.hw_gw if 1 <= b <= self.WCDMA_MAX_BAND}
            for band in sorted(wcdma_bands):
                results['WCDMA'].append(self.trace_wcdma_band(band))

        # Trace LTE bands
        for band in sorted(all_lte):
            results['LTE'].append(self.trace_lte_band(band))

        # Trace NR SA bands
        for band in sorted(all_nr):
            results['NR_SA'].append(self.trace_nr_band(band, 'SA'))

        # Trace NR NSA bands
        for band in sorted(all_nr):
            results['NR_NSA'].append(self.trace_nr_band(band, 'NSA'))

        return results
