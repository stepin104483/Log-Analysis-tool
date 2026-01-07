"""
Merge Report Generator (Stage 3)

Combines Stage 1 analysis with Stage 2 Claude review into
a single integrated HTML report.

Usage:
    python -m src.merge_report [--output OUTPUT_PATH]

This script:
1. Reads the saved analysis state from Stage 1
2. Reads Claude's review from output/claude_review.txt
3. Generates integrated HTML report with both
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.output.html_report import generate_html_report
from src.core.analyzer import AnalysisResult, AnalysisSummary
from src.core.band_tracer import BandTracer, BandTraceResult, BandStatus, FinalStatus


def load_claude_review(review_path: str) -> str:
    """Load Claude's review from file"""
    try:
        with open(review_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[WARNING] Claude review not found: {review_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read Claude review: {e}")
        return None


def load_analysis_state(state_path: str) -> dict:
    """Load saved analysis state from JSON"""
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Analysis state not found: {state_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read analysis state: {e}")
        return None


def reconstruct_analysis_result(state: dict) -> AnalysisResult:
    """Reconstruct AnalysisResult from saved state"""
    # Create tracer with document status
    tracer = BandTracer()

    # Restore document status
    from src.core.band_tracer import DocumentStatus
    for stage, status_data in state.get('doc_status', {}).items():
        tracer.doc_status[stage] = DocumentStatus(
            name=status_data['name'],
            loaded=status_data['loaded'],
            details=status_data.get('details')
        )

    # Restore MDB data for context
    tracer.mdb_lte = set(state.get('mdb_lte', []))
    tracer.mdb_nr_sa = set(state.get('mdb_nr_sa', []))
    tracer.mdb_nr_nsa = set(state.get('mdb_nr_nsa', []))

    # Reconstruct trace results
    trace_results = {}
    for band_type, results in state.get('trace_results', {}).items():
        trace_results[band_type] = []
        for r in results:
            stages = {k: BandStatus[v] for k, v in r['stages'].items()}
            trace_results[band_type].append(BandTraceResult(
                band_num=r['band_num'],
                band_type=r['band_type'],
                stages=stages,
                final_status=FinalStatus[r['final_status']],
                filtered_at=r.get('filtered_at')
            ))

    # Reconstruct summary
    s = state.get('summary', {})
    summary = AnalysisSummary(
        lte_total=s.get('lte_total', 0),
        lte_enabled=s.get('lte_enabled', 0),
        lte_filtered=s.get('lte_filtered', 0),
        lte_anomalies=s.get('lte_anomalies', 0),
        nr_sa_total=s.get('nr_sa_total', 0),
        nr_sa_enabled=s.get('nr_sa_enabled', 0),
        nr_sa_filtered=s.get('nr_sa_filtered', 0),
        nr_sa_anomalies=s.get('nr_sa_anomalies', 0),
        nr_nsa_total=s.get('nr_nsa_total', 0),
        nr_nsa_enabled=s.get('nr_nsa_enabled', 0),
        nr_nsa_filtered=s.get('nr_nsa_filtered', 0),
        nr_nsa_anomalies=s.get('nr_nsa_anomalies', 0)
    )

    # Get anomalies and errors
    anomalies = state.get('anomalies', [])
    errors = state.get('errors', [])

    return AnalysisResult(
        tracer=tracer,
        trace_results=trace_results,
        summary=summary,
        anomalies=anomalies,
        errors=errors
    )


def main():
    parser = argparse.ArgumentParser(
        description='Generate integrated HTML report (Stage 3)'
    )
    parser.add_argument(
        '--state', '-s',
        default='output/analysis_state.json',
        help='Path to analysis state JSON (default: output/analysis_state.json)'
    )
    parser.add_argument(
        '--review', '-r',
        default='output/claude_review.txt',
        help='Path to Claude review (default: output/claude_review.txt)'
    )
    parser.add_argument(
        '--output', '-o',
        default='output/band_analysis_report.html',
        help='Output HTML path (default: output/band_analysis_report.html)'
    )

    args = parser.parse_args()

    print("============================================================")
    print("         STAGE 3: Generating Integrated HTML Report")
    print("============================================================")
    print()

    # Load analysis state
    print(f"[*] Loading analysis state from: {args.state}")
    state = load_analysis_state(args.state)
    if not state:
        print("[ERROR] Cannot proceed without analysis state.")
        print("        Run Stage 1 first: python -m src.main ...")
        sys.exit(1)

    # Reconstruct analysis result
    print("[*] Reconstructing analysis result...")
    result = reconstruct_analysis_result(state)

    # Load Claude review
    print(f"[*] Loading Claude review from: {args.review}")
    claude_review = load_claude_review(args.review)
    if claude_review:
        print(f"    Review loaded: {len(claude_review)} characters")
    else:
        print("    [WARNING] No Claude review - generating report without it")

    # Generate HTML report
    print(f"[*] Generating HTML report: {args.output}")
    generate_html_report(result, args.output, claude_review)

    print()
    print("============================================================")
    print("                   REPORT GENERATED")
    print("============================================================")
    print(f"  Output: {args.output}")
    print()
    if claude_review:
        print("  Report includes Claude's expert review.")
    else:
        print("  Report generated WITHOUT Claude's review.")
    print()


if __name__ == "__main__":
    main()
