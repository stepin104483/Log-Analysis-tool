"""
Prompt Generator
Generates prompt.txt for Claude CLI review (Stage 2).

This module creates a structured prompt containing:
1. Document status
2. Automated analysis results
3. Detected anomalies
4. Knowledge base context (if available)
5. Review instructions for Claude
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .band_tracer import BandTracer, BandTraceResult, FinalStatus, BandStatus
from .analyzer import AnalysisResult, AnalysisSummary


class PromptGenerator:
    """Generates structured prompt for Claude CLI review"""

    def __init__(self, result: AnalysisResult):
        self.result = result
        self.tracer = result.tracer
        self.trace_results = result.trace_results
        self.summary = result.summary
        self.anomalies = result.anomalies

    def generate(self, output_path: Optional[str] = None,
                 knowledge_base_content: Optional[str] = None) -> str:
        """
        Generate the complete prompt.txt content.

        Args:
            output_path: Optional path to write prompt.txt
            knowledge_base_content: Optional KB context to include

        Returns:
            Complete prompt string
        """
        sections = []

        # Header
        sections.append(self._generate_header())

        # Section 1: Document Status
        sections.append(self._generate_document_status())

        # Section 2: Automated Analysis Results
        sections.append(self._generate_analysis_results())

        # Section 3: Detected Anomalies
        sections.append(self._generate_anomalies_section())

        # Section 4: Summary Statistics
        sections.append(self._generate_summary())

        # Section 5: Knowledge Base Context (if provided)
        if knowledge_base_content:
            sections.append(self._generate_kb_section(knowledge_base_content))

        # Section 6: Review Instructions
        sections.append(self._generate_review_instructions())

        prompt = '\n'.join(sections)

        # Write to file if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"[INFO] Prompt written to: {output_path}")

        return prompt

    def _generate_header(self) -> str:
        """Generate prompt header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""================================================================================
                    BAND ANALYSIS - CLAUDE REVIEW REQUEST
================================================================================

Generated: {timestamp}

You are an expert in Qualcomm modem band configuration and RF analysis.
Review the following automated band analysis and provide your expert insights.

"""

    def _generate_document_status(self) -> str:
        """Generate document status section"""
        lines = [
            "--------------------------------------------------------------------------------",
            "SECTION 1: DOCUMENT STATUS",
            "--------------------------------------------------------------------------------",
            ""
        ]

        for stage, status in self.tracer.doc_status.items():
            if status.loaded:
                icon = "[OK]     "
                details = f"- {status.details}" if status.details else "- Loaded"
            else:
                icon = "[MISSING]"
                details = "- Not provided"

            lines.append(f"{icon} {status.name:25} {details}")

        # Add impact of missing documents
        missing_docs = [s for s, st in self.tracer.doc_status.items() if not st.loaded]
        if missing_docs:
            lines.append("")
            lines.append("*** IMPACT OF MISSING DOCUMENTS ***")
            impact_messages = {
                'RFC': "Cannot verify hardware capability - using other sources as reference",
                'HW_Filter': "Hardware filter stage skipped - cannot verify HW restrictions",
                'Carrier': "Carrier policy stage skipped - cannot verify operator exclusions",
                'Generic': "Generic restrictions skipped - cannot verify FCC/regulatory blocks",
                'MDB': "MDB stage skipped - cannot verify MCC-based filtering",
                'QXDM': "Cannot verify actual device bands from QXDM 0x1CCA log",
                'UE_Cap': "Cannot verify network-reported bands"
            }
            for doc in missing_docs:
                lines.append(f"- {doc}: {impact_messages.get(doc, 'Analysis incomplete')}")

        lines.append("")
        return '\n'.join(lines)

    def _generate_analysis_results(self) -> str:
        """Generate automated analysis results section"""
        lines = [
            "--------------------------------------------------------------------------------",
            "SECTION 2: AUTOMATED ANALYSIS RESULTS",
            "--------------------------------------------------------------------------------",
            ""
        ]

        # LTE Band Tracing
        lines.append("LTE BAND TRACING:")
        lines.append(self._format_trace_table(self.trace_results.get('LTE', []), 'B'))
        lines.append("")

        # NR SA Band Tracing
        lines.append("NR SA BAND TRACING:")
        lines.append(self._format_trace_table(self.trace_results.get('NR_SA', []), 'n'))
        lines.append("")

        # NR NSA Band Tracing (only if different from SA)
        nr_nsa = self.trace_results.get('NR_NSA', [])
        nr_sa = self.trace_results.get('NR_SA', [])
        if self._results_differ(nr_sa, nr_nsa):
            lines.append("NR NSA BAND TRACING:")
            lines.append(self._format_trace_table(nr_nsa, 'n'))
            lines.append("")

        return '\n'.join(lines)

    def _format_trace_table(self, results: List[BandTraceResult], prefix: str) -> str:
        """Format trace results as a table"""
        if not results:
            return "  No bands to trace\n"

        # Header
        header = f"{'Band':<6} {'RFC':<6} {'HW':<6} {'Carrier':<8} {'Generic':<8} {'MDB':<6} {'QXDM':<6} {'UE_Cap':<7} {'Status':<15} {'Filtered At'}"
        separator = "-" * len(header)

        lines = [separator, header, separator]

        for r in results:
            band_name = f"{prefix}{r.band_num}"

            def status_symbol(s: BandStatus) -> str:
                if s == BandStatus.PASS:
                    return "PASS"
                elif s == BandStatus.FAIL:
                    return "FAIL"
                elif s == BandStatus.NA:
                    return "N/A"
                else:
                    return "SKIP"

            row = (
                f"{band_name:<6} "
                f"{status_symbol(r.stages.get('RFC', BandStatus.NA)):<6} "
                f"{status_symbol(r.stages.get('HW_Filter', BandStatus.NA)):<6} "
                f"{status_symbol(r.stages.get('Carrier', BandStatus.NA)):<8} "
                f"{status_symbol(r.stages.get('Generic', BandStatus.NA)):<8} "
                f"{status_symbol(r.stages.get('MDB', BandStatus.NA)):<6} "
                f"{status_symbol(r.stages.get('QXDM', BandStatus.NA)):<6} "
                f"{status_symbol(r.stages.get('UE_Cap', BandStatus.NA)):<7} "
                f"{r.final_status.value:<15} "
                f"{r.filtered_at or '-'}"
            )
            lines.append(row)

        lines.append(separator)
        return '\n'.join(lines)

    def _results_differ(self, sa_results: List[BandTraceResult],
                        nsa_results: List[BandTraceResult]) -> bool:
        """Check if SA and NSA results differ significantly"""
        if len(sa_results) != len(nsa_results):
            return True

        for sa, nsa in zip(sa_results, nsa_results):
            if sa.final_status != nsa.final_status:
                return True
            if sa.filtered_at != nsa.filtered_at:
                return True

        return False

    def _generate_anomalies_section(self) -> str:
        """Generate anomalies section"""
        lines = [
            "--------------------------------------------------------------------------------",
            "SECTION 3: DETECTED ANOMALIES",
            "--------------------------------------------------------------------------------",
            ""
        ]

        if not self.anomalies:
            lines.append("No anomalies detected.")
        else:
            for i, anomaly in enumerate(self.anomalies, 1):
                lines.append(f"{i}. {anomaly['band']} ({anomaly['type']}): {anomaly['reason']}")

        lines.append("")
        return '\n'.join(lines)

    def _generate_summary(self) -> str:
        """Generate summary statistics section"""
        s = self.summary
        lines = [
            "--------------------------------------------------------------------------------",
            "SECTION 4: SUMMARY STATISTICS",
            "--------------------------------------------------------------------------------",
            "",
            f"LTE Bands:    Total: {s.lte_total:3}  |  Enabled: {s.lte_enabled:3}  |  Filtered: {s.lte_filtered:3}  |  Anomalies: {s.lte_anomalies}",
            f"NR SA Bands:  Total: {s.nr_sa_total:3}  |  Enabled: {s.nr_sa_enabled:3}  |  Filtered: {s.nr_sa_filtered:3}  |  Anomalies: {s.nr_sa_anomalies}",
            f"NR NSA Bands: Total: {s.nr_nsa_total:3}  |  Enabled: {s.nr_nsa_enabled:3}  |  Filtered: {s.nr_nsa_filtered:3}  |  Anomalies: {s.nr_nsa_anomalies}",
            ""
        ]
        return '\n'.join(lines)

    def _generate_kb_section(self, kb_content: str) -> str:
        """Generate knowledge base context section"""
        lines = [
            "--------------------------------------------------------------------------------",
            "SECTION 5: RELEVANT KNOWLEDGE BASE CONTEXT",
            "--------------------------------------------------------------------------------",
            "",
            kb_content,
            ""
        ]
        return '\n'.join(lines)

    def _generate_review_instructions(self) -> str:
        """Generate review instructions for Claude"""
        section_num = "6" if self.anomalies else "5"

        lines = [
            "--------------------------------------------------------------------------------",
            f"SECTION {section_num}: REVIEW INSTRUCTIONS",
            "--------------------------------------------------------------------------------",
            "",
            "Please provide:",
            "1. Validation of the automated findings - are the PASS/FAIL determinations correct?",
            "2. Explanation for each anomaly - what are the possible root causes?",
            "3. Impact assessment - how critical is each issue?",
            "4. Recommended actions to resolve anomalies",
            "5. Overall verdict: Is this configuration safe for deployment?",
            "",
            "Format your response with clear sections for each anomaly.",
            "Use your domain knowledge of Qualcomm modem configurations to provide insights.",
            "",
            "================================================================================",
        ]
        return '\n'.join(lines)


def generate_prompt(result: AnalysisResult, output_path: Optional[str] = None,
                    kb_content: Optional[str] = None) -> str:
    """Convenience function to generate prompt"""
    generator = PromptGenerator(result)
    return generator.generate(output_path, kb_content)
