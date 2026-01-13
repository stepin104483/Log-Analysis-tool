"""
Band Analyzer
Coordinates parsing and band tracing to produce analysis results.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from ..parsers import (
    parse_rfc_xml, parse_hw_filter_xml, parse_carrier_policy_xml,
    parse_generic_restriction_xml, parse_mcfg_xml, get_all_lte_bands,
    parse_mcc2bands_xml, parse_qxdm_log, parse_ue_capability
)
from ..parsers.mcfg_parser import NV_LTE_BANDPREF, NV_NR5G_SA_BANDPREF, NV_NR5G_NSA_BANDPREF
from .band_tracer import BandTracer, BandTraceResult, FinalStatus, BandStatus


@dataclass
class AnalysisInput:
    """Input file paths for analysis"""
    rfc_path: Optional[str] = None
    hw_filter_path: Optional[str] = None
    carrier_policy_path: Optional[str] = None
    generic_restriction_path: Optional[str] = None
    mcfg_path: Optional[str] = None
    mdb_path: Optional[str] = None
    qxdm_log_path: Optional[str] = None
    ue_capability_path: Optional[str] = None
    target_mcc: Optional[str] = None  # For MDB lookup


@dataclass
class AnalysisSummary:
    """Summary statistics for analysis"""
    # GSM (2G)
    gsm_total: int = 0
    gsm_enabled: int = 0
    gsm_filtered: int = 0

    # WCDMA (3G)
    wcdma_total: int = 0
    wcdma_enabled: int = 0
    wcdma_filtered: int = 0

    # LTE (4G)
    lte_total: int = 0
    lte_enabled: int = 0
    lte_filtered: int = 0
    lte_anomalies: int = 0

    # NR SA (5G)
    nr_sa_total: int = 0
    nr_sa_enabled: int = 0
    nr_sa_filtered: int = 0
    nr_sa_anomalies: int = 0

    # NR NSA (5G)
    nr_nsa_total: int = 0
    nr_nsa_enabled: int = 0
    nr_nsa_filtered: int = 0
    nr_nsa_anomalies: int = 0


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    tracer: BandTracer
    trace_results: Dict[str, List[BandTraceResult]]
    summary: AnalysisSummary
    anomalies: List[Dict[str, Any]]
    errors: List[str]


class BandAnalyzer:
    """
    Main analyzer class that coordinates parsing and analysis.
    """

    def __init__(self):
        self.tracer = BandTracer()
        self.errors: List[str] = []

    def analyze(self, inputs: AnalysisInput) -> AnalysisResult:
        """
        Run full band analysis.

        Args:
            inputs: AnalysisInput with file paths

        Returns:
            AnalysisResult with trace results and summary
        """
        self.errors = []

        # Parse RFC
        if inputs.rfc_path:
            rfc_data = parse_rfc_xml(inputs.rfc_path)
            if rfc_data:
                self.tracer.set_rfc_bands(
                    rfc_data.lte_bands,
                    rfc_data.nr_bands,
                    rfc_data.gsm_bands,  # Include GSM bands
                    rfc_data.nr_nsa_bands  # NR bands from ca_4g_5g_combos for NSA/EN-DC
                )
            else:
                self.errors.append(f"Failed to parse RFC: {inputs.rfc_path}")

        # Parse HW Filter
        if inputs.hw_filter_path:
            hw_data = parse_hw_filter_xml(inputs.hw_filter_path)
            if hw_data:
                # Convert gw_bands from 0-indexed to 1-indexed for WCDMA
                gw_bands_1indexed = {idx + 1 for idx in hw_data.gw_bands} if hw_data.gw_bands else None
                self.tracer.set_hw_filter_bands(
                    hw_data.lte_bands,
                    hw_data.nr_sa_bands,
                    hw_data.nr_nsa_bands,
                    gw_bands_1indexed  # Include GW (GSM/WCDMA) bands
                )
            else:
                self.errors.append(f"Failed to parse HW Filter: {inputs.hw_filter_path}")

        # Parse Carrier Policy
        if inputs.carrier_policy_path:
            carrier_data = parse_carrier_policy_xml(inputs.carrier_policy_path)
            if carrier_data:
                self.tracer.set_carrier_exclusions(
                    carrier_data.lte_excluded,
                    carrier_data.nr_sa_excluded,
                    carrier_data.nr_nsa_excluded,
                    carrier_data.gw_excluded  # Include GW (GSM/WCDMA) exclusions
                )
            else:
                self.errors.append(f"Failed to parse Carrier Policy: {inputs.carrier_policy_path}")

        # Parse Generic Restrictions
        if inputs.generic_restriction_path:
            generic_data = parse_generic_restriction_xml(inputs.generic_restriction_path)
            if generic_data:
                self.tracer.set_generic_exclusions(
                    generic_data.lte_excluded,
                    generic_data.nr_sa_excluded | generic_data.nr_nsa_excluded
                )
            else:
                self.errors.append(f"Failed to parse Generic Restrictions: {inputs.generic_restriction_path}")

        # Parse MCFG NV Band Preferences
        if inputs.mcfg_path:
            mcfg_data = parse_mcfg_xml(inputs.mcfg_path)
            if mcfg_data:
                # Combine LTE bands from NV 65633 (B1-64) and NV 73680 (B65+)
                all_lte_bands = get_all_lte_bands(mcfg_data)

                # NV 73680 presence is determined by checking if lte_ext_bands is non-empty
                # (it only gets populated if NV 73680 was found)
                lte_ext_present = bool(mcfg_data.lte_ext_bands)

                self.tracer.set_nv_band_prefs(
                    lte=all_lte_bands,
                    nr_sa=mcfg_data.nr_sa_bands,
                    nr_nsa=mcfg_data.nr_nsa_bands,
                    lte_base_present=mcfg_data.nv_present[NV_LTE_BANDPREF],
                    lte_ext_present=lte_ext_present,
                    nr_sa_present=mcfg_data.nv_present[NV_NR5G_SA_BANDPREF],
                    nr_nsa_present=mcfg_data.nv_present[NV_NR5G_NSA_BANDPREF]
                )
            else:
                self.errors.append(f"Failed to parse MCFG: {inputs.mcfg_path}")

        # Parse MDB
        if inputs.mdb_path:
            mdb_data = parse_mcc2bands_xml(inputs.mdb_path, inputs.target_mcc)
            if mdb_data:
                lte_all = mdb_data.raw_values.get('l', '').lower() == 'all'
                nr_sa_all = mdb_data.raw_values.get('s', '').lower() == 'all'
                nr_nsa_all = mdb_data.raw_values.get('n', '').lower() == 'all'

                self.tracer.set_mdb_bands(
                    mdb_data.lte_bands,
                    mdb_data.nr_sa_bands,
                    mdb_data.nr_nsa_bands,
                    lte_all, nr_sa_all, nr_nsa_all
                )
            else:
                self.errors.append(f"Failed to parse MDB: {inputs.mdb_path}")

        # Parse QXDM Log
        if inputs.qxdm_log_path:
            qxdm_data = parse_qxdm_log(inputs.qxdm_log_path)
            if qxdm_data:
                self.tracer.set_qxdm_bands(
                    qxdm_data.lte_bands,
                    qxdm_data.nr_sa_bands,
                    qxdm_data.nr_nsa_bands
                )
            else:
                self.errors.append(f"Failed to parse QXDM Log: {inputs.qxdm_log_path}")

        # Parse UE Capability
        if inputs.ue_capability_path:
            ue_data = parse_ue_capability(inputs.ue_capability_path)
            if ue_data:
                self.tracer.set_ue_cap_bands(
                    ue_data.lte_bands,
                    ue_data.nr_bands,
                    nr_sa=ue_data.nr_sa_bands,    # From supportedBandListNR-SA-r15
                    nr_nsa=ue_data.nr_nsa_bands   # From supportedBandListEN-DC-r15
                )
            else:
                self.errors.append(f"Failed to parse UE Capability: {inputs.ue_capability_path}")

        # Run trace
        trace_results = self.tracer.trace_all_bands()

        # Calculate summary
        summary = self._calculate_summary(trace_results)

        # Extract anomalies
        anomalies = self._extract_anomalies(trace_results)

        return AnalysisResult(
            tracer=self.tracer,
            trace_results=trace_results,
            summary=summary,
            anomalies=anomalies,
            errors=self.errors
        )

    def _calculate_summary(self, results: Dict[str, List[BandTraceResult]]) -> AnalysisSummary:
        """Calculate summary statistics for all RAT types"""
        summary = AnalysisSummary()

        # GSM (2G)
        gsm_results = results.get('GSM', [])
        summary.gsm_total = len(gsm_results)
        for r in gsm_results:
            if r.final_status == FinalStatus.ENABLED:
                summary.gsm_enabled += 1
            elif r.final_status == FinalStatus.FILTERED:
                summary.gsm_filtered += 1

        # WCDMA (3G)
        wcdma_results = results.get('WCDMA', [])
        summary.wcdma_total = len(wcdma_results)
        for r in wcdma_results:
            if r.final_status == FinalStatus.ENABLED:
                summary.wcdma_enabled += 1
            elif r.final_status == FinalStatus.FILTERED:
                summary.wcdma_filtered += 1

        # LTE (4G)
        lte_results = results.get('LTE', [])
        summary.lte_total = len(lte_results)
        for r in lte_results:
            if r.final_status == FinalStatus.ENABLED:
                summary.lte_enabled += 1
            elif r.final_status == FinalStatus.FILTERED:
                summary.lte_filtered += 1
            elif r.final_status in [FinalStatus.ANOMALY, FinalStatus.MISSING_IN_PM, FinalStatus.MISSING_IN_UE]:
                summary.lte_anomalies += 1

        # NR SA (5G)
        nr_sa_results = results.get('NR_SA', [])
        summary.nr_sa_total = len(nr_sa_results)
        for r in nr_sa_results:
            if r.final_status == FinalStatus.ENABLED:
                summary.nr_sa_enabled += 1
            elif r.final_status == FinalStatus.FILTERED:
                summary.nr_sa_filtered += 1
            elif r.final_status in [FinalStatus.ANOMALY, FinalStatus.MISSING_IN_PM, FinalStatus.MISSING_IN_UE]:
                summary.nr_sa_anomalies += 1

        # NR NSA (5G)
        nr_nsa_results = results.get('NR_NSA', [])
        summary.nr_nsa_total = len(nr_nsa_results)
        for r in nr_nsa_results:
            if r.final_status == FinalStatus.ENABLED:
                summary.nr_nsa_enabled += 1
            elif r.final_status == FinalStatus.FILTERED:
                summary.nr_nsa_filtered += 1
            elif r.final_status in [FinalStatus.ANOMALY, FinalStatus.MISSING_IN_PM, FinalStatus.MISSING_IN_UE]:
                summary.nr_nsa_anomalies += 1

        return summary

    def _extract_anomalies(self, results: Dict[str, List[BandTraceResult]]) -> List[Dict[str, Any]]:
        """Extract all anomalies from results"""
        anomalies = []

        # Band prefix mapping
        prefix_map = {
            'GSM': 'GSM',    # GSM 850, GSM 900, etc.
            'WCDMA': 'W',    # W1, W2, etc.
            'LTE': 'B',      # B1, B2, etc.
            'NR_SA': 'n',    # n1, n77, etc.
            'NR_NSA': 'n'    # n1, n77, etc.
        }

        for band_type, band_results in results.items():
            for r in band_results:
                if r.final_status in [FinalStatus.ANOMALY, FinalStatus.MISSING_IN_PM,
                                      FinalStatus.MISSING_IN_UE, FinalStatus.NOT_SUPPORTED]:
                    # Check if it's a real anomaly (appears somewhere unexpected)
                    if r.anomaly_reason or r.final_status == FinalStatus.ANOMALY:
                        prefix = prefix_map.get(band_type, 'B')
                        anomalies.append({
                            'band': f"{prefix}{r.band_num}",
                            'type': band_type,
                            'status': r.final_status.value,
                            'reason': r.anomaly_reason or f"Status: {r.final_status.value}",
                            'stages': {k: v.value for k, v in r.stages.items()}
                        })

        return anomalies


def run_analysis(inputs: AnalysisInput) -> AnalysisResult:
    """Convenience function to run analysis"""
    analyzer = BandAnalyzer()
    return analyzer.analyze(inputs)
