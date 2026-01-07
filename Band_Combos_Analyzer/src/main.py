#!/usr/bin/env python3
"""
Band Combos Analyzer Tool - Main Entry Point

Stage 1: Automated Code Analysis
- Parses input documents
- Traces bands through filtering stages
- Generates prompt.txt for Claude CLI review

Usage:
    python main.py --rfc <rfc.xml> --hw-filter <hw_filter.xml> ...

For Stage 2 (Claude review):
    claude -p --dangerously-skip-permissions < output/prompt.txt > output/claude_review.txt
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.analyzer import BandAnalyzer, AnalysisInput
from src.core.prompt_generator import generate_prompt
from src.output.console_report import print_console_report, get_console_report
from src.output.html_report import generate_html_report


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Band Combos Analyzer Tool - Stage 1: Automated Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with all documents
  python main.py --rfc rfc.xml --hw-filter hw_filter.xml --carrier carrier_policy.xml \\
                 --generic generic_restrictions.xml --mdb mcc2bands.xml \\
                 --qxdm qxdm_log.txt --ue-cap ue_capability.txt

  # Run with only required documents
  python main.py --rfc rfc.xml --qxdm qxdm_log.txt

  # Specify output directory
  python main.py --rfc rfc.xml --output-dir ./results

Stage 2 (Claude review):
  claude -p --dangerously-skip-permissions < output/prompt.txt > output/claude_review.txt
        """
    )

    # Input files (all optional)
    parser.add_argument('--rfc', metavar='FILE',
                        help='RFC XML file (RF Card)')
    parser.add_argument('--hw-filter', metavar='FILE',
                        help='Hardware band filtering XML')
    parser.add_argument('--carrier', metavar='FILE',
                        help='Carrier policy XML')
    parser.add_argument('--generic', metavar='FILE',
                        help='Generic band restrictions XML')
    parser.add_argument('--mdb', metavar='FILE',
                        help='MDB mcc2bands XML')
    parser.add_argument('--mcc', metavar='MCC',
                        help='Target MCC for MDB lookup (e.g., 310 for US)')
    parser.add_argument('--qxdm', metavar='FILE',
                        help='QXDM log file (0x1CCA)')
    parser.add_argument('--ue-cap', metavar='FILE',
                        help='UE Capability file')

    # Output options
    parser.add_argument('--output-dir', '-o', metavar='DIR', default='output',
                        help='Output directory (default: output)')
    parser.add_argument('--prompt-file', metavar='FILE', default='prompt.txt',
                        help='Prompt file name (default: prompt.txt)')
    parser.add_argument('--html', action='store_true',
                        help='Generate HTML report')
    parser.add_argument('--no-console', action='store_true',
                        help='Suppress console output')

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Check if at least one input is provided
    inputs = [args.rfc, args.hw_filter, args.carrier, args.generic,
              args.mdb, args.qxdm, args.ue_cap]
    if not any(inputs):
        print("Error: At least one input file must be provided.")
        print("Use --help for usage information.")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build analysis input
    analysis_input = AnalysisInput(
        rfc_path=args.rfc,
        hw_filter_path=args.hw_filter,
        carrier_policy_path=args.carrier,
        generic_restriction_path=args.generic,
        mdb_path=args.mdb,
        qxdm_log_path=args.qxdm,
        ue_capability_path=args.ue_cap,
        target_mcc=args.mcc
    )

    print("=" * 60)
    print("BAND COMBOS ANALYZER - Stage 1: Automated Analysis")
    print("=" * 60)
    print()

    # Run analysis
    print("[*] Running analysis...")
    analyzer = BandAnalyzer()
    result = analyzer.analyze(analysis_input)

    # Print errors if any
    if result.errors:
        print("\n[!] Errors during parsing:")
        for error in result.errors:
            print(f"    - {error}")
        print()

    # Print console report
    if not args.no_console:
        print_console_report(result)

    # Generate prompt.txt
    prompt_path = output_dir / args.prompt_file
    print(f"\n[*] Generating prompt for Claude: {prompt_path}")
    generate_prompt(result, str(prompt_path))

    # Generate HTML report if requested
    if args.html:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = output_dir / f"band_analysis_{timestamp}.html"
        print(f"[*] Generating HTML report: {html_path}")
        generate_html_report(result, str(html_path))

    # Summary
    print("\n" + "=" * 60)
    print("STAGE 1 COMPLETE")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  - Prompt: {prompt_path}")
    if args.html:
        print(f"  - HTML:   {html_path}")

    print(f"\nTo get Claude's expert review (Stage 2), run:")
    print(f"  claude -p --dangerously-skip-permissions < {prompt_path}")

    # Return exit code based on anomalies
    total_anomalies = (result.summary.lte_anomalies +
                       result.summary.nr_sa_anomalies +
                       result.summary.nr_nsa_anomalies)

    if total_anomalies > 0:
        print(f"\n[!] {total_anomalies} anomalies detected - review recommended")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
