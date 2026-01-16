"""
HTML Report Generator for Combos Analysis

Generates HTML reports with:
- Summary dashboard
- Discrepancy tables
- Combo comparison details
- Expandable sections
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models import (
    ComboType,
    DataSource,
    DiscrepancyType,
    Discrepancy,
    AnalysisResult,
    ComparisonResult,
    ReasoningResult,
)


class HTMLReportGenerator:
    """Generate HTML reports for combo analysis results."""

    def __init__(self):
        self.report_title = "Combos Analysis Report"

    def generate(
        self,
        result: AnalysisResult,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate HTML report from analysis results.

        Args:
            result: AnalysisResult from CombosAnalyzer
            output_path: Optional path to save HTML file

        Returns:
            HTML string
        """
        html = self._build_html(result)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html

    def _build_html(self, result: AnalysisResult) -> str:
        """Build complete HTML document."""
        sections = [
            self._build_header(result),
            self._build_summary_section(result),
            self._build_reasoning_summary_section(result),
            self._build_comparison_section(result, 'rfc_vs_rrc', 'RFC vs RRC Table'),
            self._build_comparison_section(result, 'rrc_vs_uecap', 'RRC Table vs UE Capability'),
            self._build_discrepancies_section(result),
            self._build_combo_details_section(result),
            self._build_footer(),
        ]

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.report_title}</title>
    {self._get_styles()}
</head>
<body>
    <div class="container">
        {''.join(sections)}
    </div>
    {self._get_scripts()}
</body>
</html>"""

    def _build_header(self, result: AnalysisResult) -> str:
        """Build report header section."""
        files_html = ""
        if result.input_files:
            files_list = [f"<li><strong>{k}:</strong> {v}</li>" for k, v in result.input_files.items()]
            files_html = f"<ul>{''.join(files_list)}</ul>"

        return f"""
        <header>
            <h1>{self.report_title}</h1>
            <p class="timestamp">Generated: {result.timestamp}</p>
            <div class="input-files">
                <h3>Input Files</h3>
                {files_html if files_html else '<p>No input files specified</p>'}
            </div>
        </header>
        """

    def _build_summary_section(self, result: AnalysisResult) -> str:
        """Build summary dashboard section."""
        summary = result.summary

        # Combo counts
        total_rfc = summary.get('total_combos', {}).get('rfc', 0)
        total_rrc = summary.get('total_combos', {}).get('rrc', 0)
        total_uecap = summary.get('total_combos', {}).get('uecap', 0)

        # Discrepancy counts
        rfc_rrc = summary.get('comparisons', {}).get('rfc_vs_rrc', {})
        rrc_uecap = summary.get('comparisons', {}).get('rrc_vs_uecap', {})

        total_discrepancies = len(result.discrepancies)
        critical_count = len([d for d in result.discrepancies if d.severity == 'critical'])
        high_count = len([d for d in result.discrepancies if d.severity == 'high'])

        # Status color based on severity
        if critical_count > 0:
            status_class = 'status-critical'
            status_text = 'CRITICAL ISSUES FOUND'
        elif high_count > 0:
            status_class = 'status-high'
            status_text = 'HIGH PRIORITY ISSUES'
        elif total_discrepancies > 0:
            status_class = 'status-warning'
            status_text = 'DISCREPANCIES FOUND'
        else:
            status_class = 'status-ok'
            status_text = 'ALL CHECKS PASSED'

        # Match percentages
        rfc_rrc_match = rfc_rrc.get('match_percentage', 0)
        rrc_uecap_match = rrc_uecap.get('match_percentage', 0)

        return f"""
        <section class="summary">
            <h2>Summary</h2>
            <div class="status-banner {status_class}">{status_text}</div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>RFC Combos</h3>
                    <div class="stat-value">{total_rfc}</div>
                </div>
                <div class="stat-card">
                    <h3>RRC Table Combos</h3>
                    <div class="stat-value">{total_rrc}</div>
                </div>
                <div class="stat-card">
                    <h3>UE Cap Combos</h3>
                    <div class="stat-value">{total_uecap}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Discrepancies</h3>
                    <div class="stat-value {'critical' if critical_count > 0 else ''}">{total_discrepancies}</div>
                </div>
            </div>

            <div class="match-bars">
                <div class="match-bar">
                    <label>RFC vs RRC Match Rate:</label>
                    <div class="progress">
                        <div class="progress-bar" style="width: {rfc_rrc_match:.1f}%">{rfc_rrc_match:.1f}%</div>
                    </div>
                </div>
                <div class="match-bar">
                    <label>RRC vs UE Cap Match Rate:</label>
                    <div class="progress">
                        <div class="progress-bar" style="width: {rrc_uecap_match:.1f}%">{rrc_uecap_match:.1f}%</div>
                    </div>
                </div>
            </div>

            {self._build_combo_type_breakdown(result)}
        </section>
        """

    def _build_combo_type_breakdown(self, result: AnalysisResult) -> str:
        """Build combo type breakdown table."""
        by_type = result.summary.get('by_type', {})

        rows = []
        for combo_type in ComboType:
            type_data = by_type.get(combo_type.name, {})
            rows.append(f"""
                <tr>
                    <td>{combo_type.name}</td>
                    <td>{type_data.get('rfc', 0)}</td>
                    <td>{type_data.get('rrc', 0)}</td>
                    <td>{type_data.get('uecap', 0)}</td>
                </tr>
            """)

        return f"""
        <div class="breakdown-table">
            <h3>Combo Type Breakdown</h3>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>RFC</th>
                        <th>RRC Table</th>
                        <th>UE Cap</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """

    def _build_reasoning_summary_section(self, result: AnalysisResult) -> str:
        """Build reasoning summary section showing severity breakdown and explanations."""
        if not result.discrepancies:
            return ""

        # Count by severity
        severity_counts = {
            'expected': 0,
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0,
            'unknown': 0,
        }

        # Count by reason type
        reason_type_counts = {}

        # Count explained vs unexplained
        explained_count = 0
        unexplained_count = 0

        for disc in result.discrepancies:
            severity = disc.severity or 'unknown'
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            if disc.reason:
                explained_count += 1
                reason_type = disc.reason.reason_type or 'other'
                reason_type_counts[reason_type] = reason_type_counts.get(reason_type, 0) + 1
            else:
                unexplained_count += 1

        # Build severity breakdown cards
        severity_cards = []
        severity_colors = {
            'expected': '#f1f5f9',
            'low': '#f0fdf4',
            'medium': '#fef3c7',
            'high': '#fed7aa',
            'critical': '#fecaca',
            'unknown': '#e2e8f0',
        }
        severity_text_colors = {
            'expected': '#475569',
            'low': '#166534',
            'medium': '#92400e',
            'high': '#9a3412',
            'critical': '#991b1b',
            'unknown': '#64748b',
        }

        for severity, count in severity_counts.items():
            if count > 0:
                bg_color = severity_colors.get(severity, '#e2e8f0')
                text_color = severity_text_colors.get(severity, '#475569')
                severity_cards.append(f"""
                    <div class="severity-card" style="background: {bg_color}; color: {text_color};">
                        <div class="severity-label">{severity.upper()}</div>
                        <div class="severity-count">{count}</div>
                    </div>
                """)

        # Build reason type breakdown
        reason_rows = []
        for reason_type, count in sorted(reason_type_counts.items(), key=lambda x: -x[1]):
            reason_label = self._format_reason_type(reason_type)
            reason_rows.append(f"""
                <tr>
                    <td>{reason_label}</td>
                    <td>{count}</td>
                </tr>
            """)

        # Calculate explanation rate
        total_disc = len(result.discrepancies)
        explanation_rate = (explained_count / total_disc * 100) if total_disc > 0 else 0

        return f"""
        <section class="reasoning-summary">
            <h2>Reasoning Analysis</h2>

            <div class="reasoning-overview">
                <div class="explanation-rate">
                    <h3>Explanation Rate</h3>
                    <div class="progress">
                        <div class="progress-bar explanation-bar" style="width: {explanation_rate:.1f}%">
                            {explanation_rate:.1f}%
                        </div>
                    </div>
                    <p class="explanation-stats">
                        {explained_count} explained / {unexplained_count} unexplained
                    </p>
                </div>
            </div>

            <div class="severity-breakdown">
                <h3>Severity Distribution</h3>
                <div class="severity-cards">
                    {''.join(severity_cards)}
                </div>
            </div>

            {f'''
            <div class="reason-types">
                <h3>Discrepancy Reasons</h3>
                <table class="reason-table">
                    <thead>
                        <tr>
                            <th>Reason Category</th>
                            <th>Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(reason_rows)}
                    </tbody>
                </table>
            </div>
            ''' if reason_rows else ''}
        </section>
        """

    def _format_reason_type(self, reason_type: str) -> str:
        """Format reason type for display."""
        reason_labels = {
            'regional': 'Regional Band Restriction',
            'regulatory': 'Regulatory Restriction',
            'carrier_policy': 'Carrier Policy',
            'carrier_exclusion': 'Carrier Exclusion',
            'hw_variant': 'Hardware Variant Limitation',
            'efs': 'EFS Control/Pruning',
            'mmwave': 'mmWave Band Limitation',
            'firstnet': 'FirstNet (Band 14) Restriction',
            'heuristic': 'Pattern-Based Detection',
            'other': 'Other/Unclassified',
        }
        return reason_labels.get(reason_type, reason_type.replace('_', ' ').title())

    def _build_comparison_section(
        self,
        result: AnalysisResult,
        comparison_key: str,
        title: str,
    ) -> str:
        """Build comparison section for RFC vs RRC or RRC vs UE Cap."""
        comparisons = getattr(result, comparison_key, {})
        if not comparisons:
            return f"""
            <section class="comparison">
                <h2>{title}</h2>
                <p class="no-data">No comparison data available</p>
            </section>
            """

        tables = []
        for combo_type, comp_result in comparisons.items():
            if comp_result.total_discrepancies == 0 and len(comp_result.common) == 0:
                continue

            tables.append(self._build_comparison_table(combo_type, comp_result, result))

        return f"""
        <section class="comparison">
            <h2>{title}</h2>
            {''.join(tables) if tables else '<p class="no-data">No discrepancies found</p>'}
        </section>
        """

    def _build_comparison_table(
        self,
        combo_type: ComboType,
        comp_result: ComparisonResult,
        result: AnalysisResult,
    ) -> str:
        """Build comparison table for a specific combo type."""
        missing_rows = []
        extra_rows = []

        # Get combos from result
        source_a_combos = None
        source_b_combos = None

        if comp_result.source_a == DataSource.RFC:
            source_a_combos = result.rfc_combos.get(combo_type)
            source_b_combos = result.rrc_combos.get(combo_type)
        elif comp_result.source_a == DataSource.RRC_TABLE:
            source_a_combos = result.rrc_combos.get(combo_type)
            source_b_combos = result.uecap_combos.get(combo_type)

        # Missing in B (source_a has it, source_b doesn't)
        for key in sorted(comp_result.only_in_a):
            combo = source_a_combos.get(key) if source_a_combos else None
            missing_rows.append(f"""
                <tr class="missing">
                    <td>{key}</td>
                    <td>Missing in {comp_result.source_b.name}</td>
                </tr>
            """)

        # Extra in B (source_b has it, source_a doesn't)
        for key in sorted(comp_result.only_in_b):
            extra_rows.append(f"""
                <tr class="extra">
                    <td>{key}</td>
                    <td>Not in {comp_result.source_a.name}</td>
                </tr>
            """)

        all_rows = missing_rows + extra_rows

        if not all_rows:
            return ""

        return f"""
        <div class="combo-type-comparison">
            <h3>{combo_type.name}</h3>
            <p class="stats">
                Common: {len(comp_result.common)} |
                Missing: {len(comp_result.only_in_a)} |
                Extra: {len(comp_result.only_in_b)} |
                Match: {comp_result.match_percentage:.1f}%
            </p>
            <div class="table-wrapper collapsible" data-collapsed="true">
                <button class="toggle-btn" onclick="toggleTable(this)">Show Details</button>
                <table class="discrepancy-table">
                    <thead>
                        <tr>
                            <th>Combo</th>
                            <th>Issue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(all_rows[:50])}
                        {f'<tr><td colspan="2" class="more-rows">...and {len(all_rows) - 50} more</td></tr>' if len(all_rows) > 50 else ''}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def _build_discrepancies_section(self, result: AnalysisResult) -> str:
        """Build detailed discrepancies section with reasoning information."""
        if not result.discrepancies:
            return """
            <section class="discrepancies">
                <h2>Discrepancies</h2>
                <p class="no-data">No discrepancies found</p>
            </section>
            """

        # Group by type
        by_type: Dict[DiscrepancyType, List[Discrepancy]] = {}
        for disc in result.discrepancies:
            if disc.discrepancy_type not in by_type:
                by_type[disc.discrepancy_type] = []
            by_type[disc.discrepancy_type].append(disc)

        sections = []
        for disc_type, discrepancies in by_type.items():
            rows = []
            for disc in discrepancies[:100]:  # Limit to 100 per type
                severity_class = f"severity-{disc.severity}"

                # Get explanation from reasoning result
                explanation = '-'
                reason_type = ''
                if disc.reason and disc.reason.has_explanation:
                    explanation = disc.reason.explanation
                    if disc.reason.reason_type:
                        reason_type = f'<span class="reason-badge">{self._format_reason_type(disc.reason.reason_type)}</span>'

                rows.append(f"""
                    <tr class="{severity_class}">
                        <td class="combo-cell">{disc.combo}</td>
                        <td>{disc.combo.combo_type.name}</td>
                        <td><span class="severity-badge severity-{disc.severity}">{disc.severity.upper()}</span></td>
                        <td class="explanation-cell">
                            {reason_type}
                            <span class="explanation-text">{explanation}</span>
                        </td>
                    </tr>
                """)

            sections.append(f"""
                <div class="discrepancy-type">
                    <h3>{disc_type.name} ({len(discrepancies)})</h3>
                    <div class="table-wrapper collapsible" data-collapsed="false">
                        <button class="toggle-btn" onclick="toggleTable(this)">Hide</button>
                        <table class="discrepancy-table">
                            <thead>
                                <tr>
                                    <th>Combo</th>
                                    <th>Type</th>
                                    <th>Severity</th>
                                    <th>Explanation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(rows)}
                                {f'<tr><td colspan="4" class="more-rows">...and {len(discrepancies) - 100} more</td></tr>' if len(discrepancies) > 100 else ''}
                            </tbody>
                        </table>
                    </div>
                </div>
            """)

        return f"""
        <section class="discrepancies">
            <h2>Discrepancies Detail</h2>
            {''.join(sections)}
        </section>
        """

    def _build_combo_details_section(self, result: AnalysisResult) -> str:
        """Build combo details section with expandable lists."""
        # This section shows all parsed combos for reference
        sections = []

        for source_name, combos_dict in [
            ('RFC', result.rfc_combos),
            ('RRC Table', result.rrc_combos),
            ('UE Capability', result.uecap_combos),
        ]:
            if not combos_dict:
                continue

            type_sections = []
            for combo_type in ComboType:
                combo_set = combos_dict.get(combo_type)
                if not combo_set or len(combo_set) == 0:
                    continue

                combo_list = sorted([str(c) for c in combo_set.values()])[:50]
                type_sections.append(f"""
                    <div class="combo-list">
                        <h4>{combo_type.name} ({len(combo_set)})</h4>
                        <div class="collapsible" data-collapsed="true">
                            <button class="toggle-btn" onclick="toggleTable(this)">Show</button>
                            <ul>
                                {''.join(f'<li>{c}</li>' for c in combo_list)}
                                {f'<li class="more-rows">...and {len(combo_set) - 50} more</li>' if len(combo_set) > 50 else ''}
                            </ul>
                        </div>
                    </div>
                """)

            if type_sections:
                sections.append(f"""
                    <div class="source-combos">
                        <h3>{source_name}</h3>
                        {''.join(type_sections)}
                    </div>
                """)

        return f"""
        <section class="combo-details">
            <h2>Parsed Combos Reference</h2>
            {''.join(sections) if sections else '<p class="no-data">No combos parsed</p>'}
        </section>
        """

    def _build_footer(self) -> str:
        """Build report footer."""
        return f"""
        <footer>
            <p>Generated by DeviceSWAnalyzer - Combos Module</p>
            <p>Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
        """

    def _get_styles(self) -> str:
        """Get CSS styles for the report."""
        return """
        <style>
            :root {
                --primary-color: #2563eb;
                --success-color: #16a34a;
                --warning-color: #d97706;
                --danger-color: #dc2626;
                --bg-color: #f8fafc;
                --card-bg: #ffffff;
                --text-color: #1e293b;
                --border-color: #e2e8f0;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--bg-color);
                color: var(--text-color);
                line-height: 1.6;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            header {
                background: var(--card-bg);
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            h1 { color: var(--primary-color); margin-bottom: 10px; }
            h2 { color: var(--text-color); margin-bottom: 15px; border-bottom: 2px solid var(--primary-color); padding-bottom: 5px; }
            h3 { color: var(--text-color); margin-bottom: 10px; }

            .timestamp { color: #64748b; font-size: 0.9em; }

            section {
                background: var(--card-bg);
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            .status-banner {
                padding: 15px;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                margin-bottom: 20px;
            }

            .status-ok { background: #dcfce7; color: #166534; }
            .status-warning { background: #fef3c7; color: #92400e; }
            .status-high { background: #fed7aa; color: #9a3412; }
            .status-critical { background: #fecaca; color: #991b1b; }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }

            .stat-card {
                background: var(--bg-color);
                padding: 15px;
                border-radius: 6px;
                text-align: center;
            }

            .stat-card h3 { font-size: 0.9em; color: #64748b; margin-bottom: 5px; }
            .stat-value { font-size: 2em; font-weight: bold; color: var(--primary-color); }
            .stat-value.critical { color: var(--danger-color); }

            .match-bars { margin-bottom: 20px; }
            .match-bar { margin-bottom: 10px; }
            .match-bar label { display: block; margin-bottom: 5px; font-size: 0.9em; }

            .progress {
                background: var(--border-color);
                border-radius: 4px;
                height: 24px;
                overflow: hidden;
            }

            .progress-bar {
                background: var(--success-color);
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.85em;
                font-weight: bold;
                min-width: 50px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9em;
            }

            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid var(--border-color);
            }

            th { background: var(--bg-color); font-weight: 600; }

            tr.missing { background: #fef2f2; }
            tr.extra { background: #fefce8; }

            .severity-critical { background: #fecaca; }
            .severity-high { background: #fed7aa; }
            .severity-medium { background: #fef3c7; }
            .severity-low { background: #f0fdf4; }
            .severity-expected { background: #f1f5f9; }

            .no-data { color: #64748b; font-style: italic; }
            .more-rows { color: #64748b; font-style: italic; text-align: center; }

            .toggle-btn {
                background: var(--primary-color);
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.85em;
                margin-bottom: 10px;
            }

            .toggle-btn:hover { opacity: 0.9; }

            .collapsible[data-collapsed="true"] table,
            .collapsible[data-collapsed="true"] ul {
                display: none;
            }

            .combo-list ul {
                list-style: none;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 5px;
            }

            .combo-list li {
                background: var(--bg-color);
                padding: 5px 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.85em;
            }

            /* Reasoning Summary Styles */
            .reasoning-summary {
                background: linear-gradient(135deg, var(--card-bg) 0%, #f8fafc 100%);
            }

            .reasoning-overview {
                margin-bottom: 20px;
            }

            .explanation-rate {
                background: var(--bg-color);
                padding: 15px;
                border-radius: 6px;
            }

            .explanation-rate h3 {
                margin-bottom: 10px;
                font-size: 0.95em;
            }

            .explanation-bar {
                background: var(--primary-color);
            }

            .explanation-stats {
                margin-top: 8px;
                font-size: 0.85em;
                color: #64748b;
            }

            .severity-breakdown {
                margin-bottom: 20px;
            }

            .severity-cards {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }

            .severity-card {
                padding: 12px 20px;
                border-radius: 6px;
                text-align: center;
                min-width: 100px;
            }

            .severity-label {
                font-size: 0.75em;
                font-weight: 600;
                letter-spacing: 0.5px;
            }

            .severity-count {
                font-size: 1.5em;
                font-weight: bold;
                margin-top: 4px;
            }

            .reason-types {
                margin-top: 20px;
            }

            .reason-table {
                max-width: 400px;
            }

            .reason-table th:first-child,
            .reason-table td:first-child {
                width: 70%;
            }

            /* Discrepancy Table Enhancements */
            .severity-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.75em;
                font-weight: 600;
            }

            .severity-badge.severity-expected { background: #f1f5f9; color: #475569; }
            .severity-badge.severity-low { background: #dcfce7; color: #166534; }
            .severity-badge.severity-medium { background: #fef3c7; color: #92400e; }
            .severity-badge.severity-high { background: #fed7aa; color: #9a3412; }
            .severity-badge.severity-critical { background: #fecaca; color: #991b1b; }
            .severity-badge.severity-unknown { background: #e2e8f0; color: #64748b; }

            .reason-badge {
                display: inline-block;
                background: #e0e7ff;
                color: #3730a3;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.7em;
                font-weight: 500;
                margin-right: 6px;
                vertical-align: middle;
            }

            .combo-cell {
                font-family: monospace;
                font-size: 0.9em;
            }

            .explanation-cell {
                max-width: 400px;
            }

            .explanation-text {
                font-size: 0.85em;
                color: #475569;
            }

            .discrepancy-type {
                margin-bottom: 20px;
            }

            .discrepancy-type h3 {
                margin-bottom: 10px;
            }

            footer {
                text-align: center;
                padding: 20px;
                color: #64748b;
                font-size: 0.85em;
            }

            @media (max-width: 768px) {
                .stats-grid { grid-template-columns: repeat(2, 1fr); }
                .stat-value { font-size: 1.5em; }
            }
        </style>
        """

    def _get_scripts(self) -> str:
        """Get JavaScript for interactive elements."""
        return """
        <script>
            function toggleTable(btn) {
                const container = btn.parentElement;
                const isCollapsed = container.getAttribute('data-collapsed') === 'true';
                container.setAttribute('data-collapsed', !isCollapsed);
                btn.textContent = isCollapsed ? 'Hide' : 'Show Details';
            }
        </script>
        """


def generate_html_report(
    result: AnalysisResult,
    output_path: Optional[str] = None,
) -> str:
    """
    Convenience function to generate HTML report.

    Args:
        result: AnalysisResult from CombosAnalyzer
        output_path: Optional path to save HTML file

    Returns:
        HTML string
    """
    generator = HTMLReportGenerator()
    return generator.generate(result, output_path)
