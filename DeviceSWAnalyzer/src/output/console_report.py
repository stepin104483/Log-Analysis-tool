"""
Console Report Generator
Generates formatted console output for band analysis results.
"""

from typing import Dict, List
from ..core.band_tracer import BandTraceResult, BandStatus, FinalStatus
from ..core.analyzer import AnalysisResult


class ConsoleReport:
    """Generates formatted console output"""

    # Status symbols (ASCII-friendly for Windows compatibility)
    PASS_SYMBOL = "[OK]"
    FAIL_SYMBOL = "[X]"
    NA_SYMBOL = "[-]"
    SKIP_SYMBOL = "[.]"

    def __init__(self, result: AnalysisResult):
        self.result = result
        self.tracer = result.tracer
        self.trace_results = result.trace_results
        self.summary = result.summary
        self.anomalies = result.anomalies

    def generate(self) -> str:
        """Generate complete console report"""
        sections = []

        sections.append(self._header())
        sections.append(self._document_status())
        sections.append(self._band_tracing_lte())
        sections.append(self._band_tracing_nr_sa())

        # NR NSA only if different from SA
        if self._nr_nsa_differs():
            sections.append(self._band_tracing_nr_nsa())

        sections.append(self._anomalies_section())
        sections.append(self._summary_section())
        sections.append(self._footer())

        return '\n'.join(sections)

    def print_report(self):
        """Print report to console"""
        print(self.generate())

    def _header(self) -> str:
        return """
================================================================================
                         BAND ANALYSIS REPORT
================================================================================
"""

    def _document_status(self) -> str:
        lines = [
            "DOCUMENT STATUS",
            "-" * 60
        ]

        for stage, status in self.tracer.doc_status.items():
            if status.loaded:
                icon = self.PASS_SYMBOL
                details = status.details if status.details else "Loaded"
            else:
                icon = self.FAIL_SYMBOL
                details = "Not provided"

            lines.append(f"  {icon} {status.name:25} - {details}")

        lines.append("-" * 60)
        lines.append("")
        return '\n'.join(lines)

    def _band_tracing_lte(self) -> str:
        results = self.trace_results.get('LTE', [])
        return self._format_band_table("LTE", results, 'B')

    def _band_tracing_nr_sa(self) -> str:
        results = self.trace_results.get('NR_SA', [])
        return self._format_band_table("NR SA", results, 'n')

    def _band_tracing_nr_nsa(self) -> str:
        results = self.trace_results.get('NR_NSA', [])
        return self._format_band_table("NR NSA", results, 'n')

    def _nr_nsa_differs(self) -> bool:
        """Check if NR NSA results differ from SA"""
        sa = self.trace_results.get('NR_SA', [])
        nsa = self.trace_results.get('NR_NSA', [])

        if len(sa) != len(nsa):
            return True

        for s, n in zip(sa, nsa):
            if s.final_status != n.final_status or s.filtered_at != n.filtered_at:
                return True

        return False

    def _format_band_table(self, title: str, results: List[BandTraceResult], prefix: str) -> str:
        if not results:
            return f"\nBAND TRACING - {title}\n  No bands to trace\n"

        lines = [
            f"\nBAND TRACING - {title}",
            "-" * 90
        ]

        # Header (6 stages: RFC → HW → Carrier → Generic → QXDM → UE Cap)
        header = f"{'Band':<6} {'RFC':<5} {'HW':<5} {'Carrier':<8} {'Generic':<8} {'QXDM':<5} {'UECap':<6} {'Status':<15} {'Filtered At'}"
        lines.append(header)
        lines.append("-" * 90)

        for r in results:
            band_name = f"{prefix}{r.band_num}"

            def sym(s: BandStatus) -> str:
                if s == BandStatus.PASS:
                    return "OK"
                elif s == BandStatus.FAIL:
                    return "X"
                elif s == BandStatus.NA:
                    return "-"
                return "."

            # Color/highlight anomalies in the status
            status_str = r.final_status.value
            if r.final_status in [FinalStatus.ANOMALY, FinalStatus.MISSING_IN_PM]:
                status_str = f"*{status_str}*"

            row = (
                f"{band_name:<6} "
                f"{sym(r.stages.get('RFC', BandStatus.NA)):<5} "
                f"{sym(r.stages.get('HW_Filter', BandStatus.NA)):<5} "
                f"{sym(r.stages.get('Carrier', BandStatus.NA)):<8} "
                f"{sym(r.stages.get('Generic', BandStatus.NA)):<8} "
                f"{sym(r.stages.get('QXDM', BandStatus.NA)):<5} "
                f"{sym(r.stages.get('UE_Cap', BandStatus.NA)):<6} "
                f"{status_str:<15} "
                f"{r.filtered_at or '-'}"
            )
            lines.append(row)

        lines.append("-" * 90)
        return '\n'.join(lines)

    def _anomalies_section(self) -> str:
        lines = ["\n"]

        if self.anomalies:
            lines.append("*** ANOMALIES DETECTED ***")
            lines.append("-" * 60)
            for anomaly in self.anomalies:
                lines.append(f"  - {anomaly['band']} ({anomaly['type']}): {anomaly['reason']}")
            lines.append("-" * 60)
        else:
            lines.append("No anomalies detected.")

        lines.append("")
        return '\n'.join(lines)

    def _summary_section(self) -> str:
        s = self.summary
        lines = [
            "SUMMARY",
            "-" * 60,
            f"  LTE:    {s.lte_enabled} enabled / {s.lte_total} total  ({s.lte_filtered} filtered, {s.lte_anomalies} anomalies)",
            f"  NR SA:  {s.nr_sa_enabled} enabled / {s.nr_sa_total} total  ({s.nr_sa_filtered} filtered, {s.nr_sa_anomalies} anomalies)",
            f"  NR NSA: {s.nr_nsa_enabled} enabled / {s.nr_nsa_total} total  ({s.nr_nsa_filtered} filtered, {s.nr_nsa_anomalies} anomalies)",
            "-" * 60
        ]
        return '\n'.join(lines)

    def _footer(self) -> str:
        total_anomalies = self.summary.lte_anomalies + self.summary.nr_sa_anomalies + self.summary.nr_nsa_anomalies

        if total_anomalies > 0:
            verdict = f"*** {total_anomalies} ANOMALIES REQUIRE INVESTIGATION ***"
        else:
            verdict = "Configuration appears correct."

        return f"""
================================================================================
{verdict}

To get Claude's expert review, run:
  claude -p --dangerously-skip-permissions < output/prompt.txt

================================================================================
"""


def print_console_report(result: AnalysisResult):
    """Convenience function to print console report"""
    report = ConsoleReport(result)
    report.print_report()


def get_console_report(result: AnalysisResult) -> str:
    """Convenience function to get console report as string"""
    report = ConsoleReport(result)
    return report.generate()
