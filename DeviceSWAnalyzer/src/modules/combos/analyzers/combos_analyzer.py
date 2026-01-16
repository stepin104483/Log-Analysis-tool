"""
Combos Analyzer - Main Analysis Orchestrator

Coordinates parsing and comparison of combo data from multiple sources:
- RFC XML (expected combos)
- QXDM 0xB826 (built RRC table)
- UE Capability (advertised combos)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    ComboSet,
    Discrepancy,
    ComparisonResult,
    AnalysisResult,
)
from ..parsers import RFCParser, QXDMParser, UECapParser
from .normalizer import Normalizer
from .comparator import Comparator


class CombosAnalyzer:
    """
    Main analyzer for combo comparison across sources.

    Orchestrates:
    1. Parsing input files (RFC, QXDM, UE Cap)
    2. Normalizing combo data
    3. Comparing across sources
    4. Generating discrepancy reports
    """

    def __init__(self):
        self.rfc_parser = RFCParser()
        self.qxdm_parser = QXDMParser()
        self.uecap_parser = UECapParser()
        self.comparator = Comparator()

        # Analysis state
        self._rfc_combos: Optional[Dict[ComboType, ComboSet]] = None
        self._rrc_combos: Optional[Dict[ComboType, ComboSet]] = None
        self._uecap_combos: Optional[Dict[ComboType, ComboSet]] = None

        # Results
        self._rfc_vs_rrc: Optional[Dict[ComboType, ComparisonResult]] = None
        self._rrc_vs_uecap: Optional[Dict[ComboType, ComparisonResult]] = None
        self._all_discrepancies: List[Discrepancy] = []

        # Parse errors from all sources
        self._parse_errors: List[str] = []

    def analyze(
        self,
        rfc_file: Optional[str] = None,
        qxdm_file: Optional[str] = None,
        uecap_file: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Run complete combo analysis.

        Args:
            rfc_file: Path to RFC XML file
            qxdm_file: Path to QXDM 0xB826 text export
            uecap_file: Path to UE Capability data (P1)

        Returns:
            AnalysisResult with all parsed data, comparisons, and discrepancies
        """
        self._reset_state()

        result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
        )

        # Track input files
        if rfc_file:
            result.input_files['rfc'] = str(Path(rfc_file).name)
        if qxdm_file:
            result.input_files['qxdm'] = str(Path(qxdm_file).name)
        if uecap_file:
            result.input_files['uecap'] = str(Path(uecap_file).name)

        # Parse RFC combos
        if rfc_file:
            self._rfc_combos = self._parse_rfc(rfc_file)
            result.rfc_combos = self._rfc_combos

        # Parse QXDM 0xB826 combos
        if qxdm_file:
            self._rrc_combos = self._parse_qxdm(qxdm_file)
            result.rrc_combos = self._rrc_combos

        # UE Capability parsing (P1 - placeholder)
        if uecap_file:
            self._uecap_combos = self._parse_uecap(uecap_file)
            result.uecap_combos = self._uecap_combos

        # Compare RFC vs RRC
        if self._rfc_combos and self._rrc_combos:
            self._rfc_vs_rrc, discrepancies = self.comparator.compare_rfc_vs_rrc(
                self._rfc_combos, self._rrc_combos
            )
            result.rfc_vs_rrc = self._rfc_vs_rrc
            self._all_discrepancies.extend(discrepancies)

        # Compare RRC vs UE Cap
        if self._rrc_combos and self._uecap_combos:
            self._rrc_vs_uecap, discrepancies = self.comparator.compare_rrc_vs_uecap(
                self._rrc_combos, self._uecap_combos
            )
            result.rrc_vs_uecap = self._rrc_vs_uecap
            self._all_discrepancies.extend(discrepancies)

        # Store all discrepancies in result
        result.discrepancies = self._all_discrepancies

        # Generate summary statistics
        result.summary = self.comparator.generate_summary_stats(
            self._rfc_combos,
            self._rrc_combos,
            self._uecap_combos,
            self._rfc_vs_rrc,
            self._rrc_vs_uecap,
        )

        # Add parse errors to summary
        result.summary['parse_errors'] = self._parse_errors

        return result

    def _reset_state(self):
        """Reset internal state for new analysis."""
        self._rfc_combos = None
        self._rrc_combos = None
        self._uecap_combos = None
        self._rfc_vs_rrc = None
        self._rrc_vs_uecap = None
        self._all_discrepancies = []
        self._parse_errors = []

    def _parse_rfc(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """Parse RFC XML file."""
        combos = self.rfc_parser.parse(file_path)

        # Collect parse errors
        errors = self.rfc_parser.get_parse_errors()
        for error in errors:
            self._parse_errors.append(f"RFC: {error}")

        # Normalize all combo sets
        normalized = {}
        for combo_type, combo_set in combos.items():
            normalized[combo_type] = Normalizer.normalize_combo_set(combo_set)

        return normalized

    def _parse_qxdm(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """Parse QXDM 0xB826 file."""
        combos = self.qxdm_parser.parse(file_path)

        # Collect parse errors
        errors = self.qxdm_parser.get_parse_errors()
        for error in errors:
            self._parse_errors.append(f"QXDM: {error}")

        # Normalize all combo sets
        normalized = {}
        for combo_type, combo_set in combos.items():
            normalized[combo_type] = Normalizer.normalize_combo_set(combo_set)

        return normalized

    def _parse_uecap(self, file_path: str) -> Dict[ComboType, ComboSet]:
        """
        Parse UE Capability XML file.

        Args:
            file_path: Path to UE Capability XML file

        Returns:
            Dict mapping ComboType to normalized ComboSet
        """
        combos = self.uecap_parser.parse(file_path)

        # Collect parse errors
        errors = self.uecap_parser.get_parse_errors()
        for error in errors:
            self._parse_errors.append(f"UE Cap: {error}")

        # Normalize all combo sets
        normalized = {}
        for combo_type, combo_set in combos.items():
            normalized[combo_type] = Normalizer.normalize_combo_set(combo_set)

        return normalized

    def get_discrepancies_by_severity(self, severity: str) -> List[Discrepancy]:
        """Get discrepancies filtered by severity level."""
        return [d for d in self._all_discrepancies if d.severity == severity]

    def get_discrepancies_by_type(self, disc_type: DiscrepancyType) -> List[Discrepancy]:
        """Get discrepancies filtered by discrepancy type."""
        return [d for d in self._all_discrepancies if d.discrepancy_type == disc_type]

    def get_high_priority_issues(self) -> List[Discrepancy]:
        """Get critical and high severity discrepancies."""
        return [
            d for d in self._all_discrepancies
            if d.severity in ['critical', 'high']
        ]

    def get_parse_errors(self) -> List[str]:
        """Get all parse errors from analysis."""
        return self._parse_errors

    def get_combo_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Get combo counts by source and type.

        Returns:
            Dict like {'rfc': {'LTE_CA': 100, 'ENDC': 50}, ...}
        """
        counts = {
            'rfc': {},
            'rrc': {},
            'uecap': {},
        }

        if self._rfc_combos:
            for combo_type, combo_set in self._rfc_combos.items():
                counts['rfc'][combo_type.name] = len(combo_set)

        if self._rrc_combos:
            for combo_type, combo_set in self._rrc_combos.items():
                counts['rrc'][combo_type.name] = len(combo_set)

        if self._uecap_combos:
            for combo_type, combo_set in self._uecap_combos.items():
                counts['uecap'][combo_type.name] = len(combo_set)

        return counts

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert analysis results to dictionary for serialization.

        Returns:
            Dict representation of analysis results
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'combo_counts': self.get_combo_counts(),
            'discrepancies': {
                'total': len(self._all_discrepancies),
                'by_type': {},
                'by_severity': {},
            },
            'parse_errors': self._parse_errors,
        }

        # Count by discrepancy type
        for disc_type in DiscrepancyType:
            count = len([d for d in self._all_discrepancies if d.discrepancy_type == disc_type])
            if count > 0:
                result['discrepancies']['by_type'][disc_type.name] = count

        # Count by severity
        for severity in ['critical', 'high', 'medium', 'low', 'expected', 'unknown']:
            count = len([d for d in self._all_discrepancies if d.severity == severity])
            if count > 0:
                result['discrepancies']['by_severity'][severity] = count

        return result


def analyze_combos(
    rfc_file: Optional[str] = None,
    qxdm_file: Optional[str] = None,
    uecap_file: Optional[str] = None,
) -> AnalysisResult:
    """
    Convenience function to run combo analysis.

    Args:
        rfc_file: Path to RFC XML file
        qxdm_file: Path to QXDM 0xB826 text export
        uecap_file: Path to UE Capability data

    Returns:
        AnalysisResult with all analysis data
    """
    analyzer = CombosAnalyzer()
    return analyzer.analyze(rfc_file, qxdm_file, uecap_file)
