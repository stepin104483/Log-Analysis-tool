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

    Stages:
    1. RFC - RF Card supported bands
    2. HW Filter - Hardware band filtering
    3. Carrier - Carrier policy exclusions
    4. Generic - FCC/regulatory restrictions
    5. MDB - MCC-based filtering
    6. QXDM - Actual device bands (0x1CCA)
    7. UE Cap - Network-reported bands
    """

    STAGES = ['RFC', 'HW_Filter', 'Carrier', 'Generic', 'MDB', 'QXDM', 'UE_Cap']

    def __init__(self):
        # Bands from each source
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
        self.ue_cap_nr: Set[int] = set()

        # Document status
        self.doc_status: Dict[str, DocumentStatus] = {
            'RFC': DocumentStatus('RFC XML', False),
            'HW_Filter': DocumentStatus('HW Band Filtering', False),
            'Carrier': DocumentStatus('Carrier Policy', False),
            'Generic': DocumentStatus('Generic Restrictions', False),
            'MDB': DocumentStatus('MDB Config', False),
            'QXDM': DocumentStatus('QXDM Log', False),
            'UE_Cap': DocumentStatus('UE Capability', False),
        }

    def set_rfc_bands(self, lte_bands: Set[int], nr_bands: Set[int]):
        """Set RFC bands"""
        self.rfc_lte = lte_bands
        self.rfc_nr = nr_bands
        self.doc_status['RFC'].loaded = True
        self.doc_status['RFC'].band_count = len(lte_bands) + len(nr_bands)
        self.doc_status['RFC'].details = f"{len(lte_bands)} LTE, {len(nr_bands)} NR"

    def set_hw_filter_bands(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int]):
        """Set HW filter allowed bands"""
        self.hw_lte = lte
        self.hw_nr_sa = nr_sa
        self.hw_nr_nsa = nr_nsa
        self.doc_status['HW_Filter'].loaded = True
        self.doc_status['HW_Filter'].details = "Loaded"

    def set_carrier_exclusions(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int]):
        """Set carrier policy excluded bands"""
        self.carrier_lte_excluded = lte
        self.carrier_nr_sa_excluded = nr_sa
        self.carrier_nr_nsa_excluded = nr_nsa
        self.doc_status['Carrier'].loaded = True
        self.doc_status['Carrier'].details = f"Excl: {len(lte)} LTE, {len(nr_sa)} NR"

    def set_generic_exclusions(self, lte: Set[int], nr: Set[int]):
        """Set generic restriction excluded bands"""
        self.generic_lte_excluded = lte
        self.generic_nr_excluded = nr
        self.doc_status['Generic'].loaded = True
        self.doc_status['Generic'].details = f"Excl: {len(lte)} LTE, {len(nr)} NR"

    def set_mdb_bands(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int],
                      lte_all: bool = False, nr_sa_all: bool = False, nr_nsa_all: bool = False):
        """Set MDB allowed bands"""
        self.mdb_lte = lte
        self.mdb_nr_sa = nr_sa
        self.mdb_nr_nsa = nr_nsa
        self.mdb_lte_all = lte_all
        self.mdb_nr_sa_all = nr_sa_all
        self.mdb_nr_nsa_all = nr_nsa_all
        self.doc_status['MDB'].loaded = True
        self.doc_status['MDB'].details = "Loaded"

    def set_qxdm_bands(self, lte: Set[int], nr_sa: Set[int], nr_nsa: Set[int]):
        """Set QXDM 0x1CCA bands"""
        self.qxdm_lte = lte
        self.qxdm_nr_sa = nr_sa
        self.qxdm_nr_nsa = nr_nsa
        self.doc_status['QXDM'].loaded = True
        self.doc_status['QXDM'].band_count = len(lte) + len(nr_sa)
        self.doc_status['QXDM'].details = f"{len(lte)} LTE, {len(nr_sa)} NR SA"

    def set_ue_cap_bands(self, lte: Set[int], nr: Set[int]):
        """Set UE Capability bands"""
        self.ue_cap_lte = lte
        self.ue_cap_nr = nr
        self.doc_status['UE_Cap'].loaded = True
        self.doc_status['UE_Cap'].band_count = len(lte) + len(nr)
        self.doc_status['UE_Cap'].details = f"{len(lte)} LTE, {len(nr)} NR"

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

        # Stage 5: MDB
        if filtered:
            result.stages['MDB'] = BandStatus.SKIPPED
        elif not self.doc_status['MDB'].loaded:
            result.stages['MDB'] = BandStatus.NA
        else:
            if self.mdb_lte_all or band in self.mdb_lte:
                result.stages['MDB'] = BandStatus.PASS
            else:
                result.stages['MDB'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'MDB'

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
        mdb_bands = self.mdb_nr_sa if mode == 'SA' else self.mdb_nr_nsa
        mdb_all = self.mdb_nr_sa_all if mode == 'SA' else self.mdb_nr_nsa_all
        qxdm_bands = self.qxdm_nr_sa if mode == 'SA' else self.qxdm_nr_nsa

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

        # Stage 5: MDB
        if filtered:
            result.stages['MDB'] = BandStatus.SKIPPED
        elif not self.doc_status['MDB'].loaded:
            result.stages['MDB'] = BandStatus.NA
        else:
            if mdb_all or band in mdb_bands:
                result.stages['MDB'] = BandStatus.PASS
            else:
                result.stages['MDB'] = BandStatus.FAIL
                filtered = True
                result.filtered_at = 'MDB'

        # Stage 6: QXDM
        if not self.doc_status['QXDM'].loaded:
            result.stages['QXDM'] = BandStatus.NA
        else:
            if band in qxdm_bands:
                result.stages['QXDM'] = BandStatus.PASS
            else:
                result.stages['QXDM'] = BandStatus.FAIL

        # Stage 7: UE Capability
        if not self.doc_status['UE_Cap'].loaded:
            result.stages['UE_Cap'] = BandStatus.NA
        else:
            if band in self.ue_cap_nr:
                result.stages['UE_Cap'] = BandStatus.PASS
            else:
                result.stages['UE_Cap'] = BandStatus.FAIL

        # Determine final status
        result.final_status = self._determine_final_status(result, filtered)

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
        """Get union of all bands from all sources for comprehensive analysis"""
        all_lte = (self.rfc_lte | self.qxdm_lte | self.ue_cap_lte |
                   self.hw_lte | self.mdb_lte)
        all_nr = (self.rfc_nr | self.qxdm_nr_sa | self.qxdm_nr_nsa |
                  self.ue_cap_nr | self.hw_nr_sa | self.hw_nr_nsa |
                  self.mdb_nr_sa | self.mdb_nr_nsa)
        return all_lte, all_nr

    def trace_all_bands(self) -> Dict[str, List[BandTraceResult]]:
        """Trace all bands from all sources"""
        results = {
            'LTE': [],
            'NR_SA': [],
            'NR_NSA': []
        }

        # Get all unique bands
        all_lte, all_nr = self.get_all_bands()

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
