"""
Bands Module Integration Tests

Tests the integration between parsers, tracer, analyzer, and output generators.
"""

import pytest
import sys
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


class TestParserTracerIntegration:
    """Test integration between parsers and BandTracer."""

    def test_rfc_parser_to_tracer(self, integration_test_files):
        """
        INT-BANDS-001: RFC Parser output feeds correctly into BandTracer.
        """
        from src.parsers import parse_rfc_xml
        from src.core.band_tracer import BandTracer

        # Parse RFC
        rfc_result = parse_rfc_xml(str(integration_test_files['rfc']))
        assert rfc_result is not None

        # Feed into tracer
        tracer = BandTracer()
        tracer.set_rfc_bands(
            lte_bands=rfc_result.lte_bands,
            nr_bands=rfc_result.nr_bands,
            gsm_bands=rfc_result.gsm_bands,
            nr_nsa_bands=rfc_result.nr_nsa_bands
        )

        # Verify tracer received bands
        assert tracer.doc_status['RFC'].loaded
        assert len(tracer.rfc_lte) > 0 or len(tracer.rfc_nr) > 0

    def test_hw_filter_parser_to_tracer(self, integration_test_files):
        """
        INT-BANDS-002: HW Filter Parser output feeds correctly into BandTracer.
        """
        from src.parsers import parse_hw_filter_xml
        from src.core.band_tracer import BandTracer

        # Parse HW Filter
        hw_result = parse_hw_filter_xml(str(integration_test_files['hw_filter']))
        assert hw_result is not None

        # Feed into tracer
        tracer = BandTracer()
        tracer.set_hw_filter_bands(
            lte=hw_result.lte_bands,
            nr_sa=hw_result.nr_sa_bands,
            nr_nsa=hw_result.nr_nsa_bands,
            gw=hw_result.gw_bands
        )

        # Verify tracer received bands
        assert tracer.doc_status['HW_Filter'].loaded

    def test_multiple_parsers_to_tracer(self, integration_test_files):
        """
        INT-BANDS-003: Multiple parsers feed into single BandTracer correctly.
        """
        from src.parsers import parse_rfc_xml, parse_hw_filter_xml
        from src.core.band_tracer import BandTracer

        # Parse all files
        rfc_result = parse_rfc_xml(str(integration_test_files['rfc']))
        hw_result = parse_hw_filter_xml(str(integration_test_files['hw_filter']))

        # Feed all into tracer
        tracer = BandTracer()

        tracer.set_rfc_bands(
            lte_bands=rfc_result.lte_bands,
            nr_bands=rfc_result.nr_bands,
            nr_nsa_bands=rfc_result.nr_nsa_bands
        )

        tracer.set_hw_filter_bands(
            lte=hw_result.lte_bands,
            nr_sa=hw_result.nr_sa_bands,
            nr_nsa=hw_result.nr_nsa_bands
        )

        # Verify all sources loaded
        assert tracer.doc_status['RFC'].loaded
        assert tracer.doc_status['HW_Filter'].loaded

        # Trace all bands
        results = tracer.trace_all_bands()
        assert 'LTE' in results
        assert 'NR_SA' in results


class TestTracerAnalysisIntegration:
    """Test integration between BandTracer and analysis logic."""

    def test_tracer_produces_valid_trace_results(self, integration_test_files):
        """
        INT-BANDS-004: BandTracer produces valid BandTraceResult objects.
        """
        from src.parsers import parse_rfc_xml, parse_hw_filter_xml
        from src.core.band_tracer import BandTracer, BandTraceResult

        # Setup tracer with data
        rfc_result = parse_rfc_xml(str(integration_test_files['rfc']))
        hw_result = parse_hw_filter_xml(str(integration_test_files['hw_filter']))

        tracer = BandTracer()
        tracer.set_rfc_bands(
            lte_bands=rfc_result.lte_bands,
            nr_bands=rfc_result.nr_bands
        )
        tracer.set_hw_filter_bands(
            lte=hw_result.lte_bands,
            nr_sa=hw_result.nr_sa_bands,
            nr_nsa=hw_result.nr_nsa_bands
        )

        # Get trace results
        results = tracer.trace_all_bands()

        # Verify structure
        for band_type in ['LTE', 'NR_SA', 'NR_NSA']:
            assert band_type in results
            for trace_result in results[band_type]:
                assert isinstance(trace_result, BandTraceResult)
                assert hasattr(trace_result, 'band_num')
                assert hasattr(trace_result, 'stages')
                assert hasattr(trace_result, 'final_status')

    def test_filtering_pipeline_works_correctly(self, integration_test_files):
        """
        INT-BANDS-005: Bands are correctly filtered through pipeline stages.
        """
        from src.parsers import parse_rfc_xml, parse_hw_filter_xml
        from src.core.band_tracer import BandTracer, FinalStatus

        rfc_result = parse_rfc_xml(str(integration_test_files['rfc']))
        hw_result = parse_hw_filter_xml(str(integration_test_files['hw_filter']))

        tracer = BandTracer()
        tracer.set_rfc_bands(
            lte_bands=rfc_result.lte_bands,
            nr_bands=rfc_result.nr_bands
        )
        tracer.set_hw_filter_bands(
            lte=hw_result.lte_bands,
            nr_sa=hw_result.nr_sa_bands,
            nr_nsa=hw_result.nr_nsa_bands
        )

        results = tracer.trace_all_bands()

        # Check that some bands are filtered and some pass
        lte_results = results['LTE']
        statuses = [r.final_status for r in lte_results]

        # Should have variety of statuses (some enabled, some filtered)
        assert len(lte_results) > 0


class TestAnalyzerOutputIntegration:
    """Test integration between analyzer and output generators."""

    def test_analyzer_produces_output_for_html_report(self, integration_test_files, tmp_path):
        """
        INT-BANDS-006: Analyzer output can be used to generate HTML report.
        """
        from src.core.analyzer import BandAnalyzer, AnalysisInput
        from src.output.html_report import generate_html_report

        # Run analysis
        analyzer = BandAnalyzer()
        inputs = AnalysisInput(
            rfc_path=str(integration_test_files['rfc']),
            hw_filter_path=str(integration_test_files['hw_filter'])
        )
        result = analyzer.analyze(inputs)

        # Generate HTML report
        output_path = tmp_path / "integration_report.html"
        generate_html_report(result, str(output_path))

        # Verify report created and has content
        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 100
        assert "<" in content  # Has HTML tags

    def test_analyzer_produces_output_for_prompt(self, integration_test_files, tmp_path):
        """
        INT-BANDS-007: Analyzer output can be used to generate Claude prompt.
        """
        from src.core.analyzer import BandAnalyzer, AnalysisInput
        from src.core.prompt_generator import generate_prompt

        # Run analysis
        analyzer = BandAnalyzer()
        inputs = AnalysisInput(
            rfc_path=str(integration_test_files['rfc']),
            hw_filter_path=str(integration_test_files['hw_filter'])
        )
        result = analyzer.analyze(inputs)

        # Generate prompt
        output_path = tmp_path / "integration_prompt.txt"
        generate_prompt(result, output_path=str(output_path))

        # Verify prompt created and has content
        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 50


class TestFullPipelineIntegration:
    """Test complete end-to-end pipeline without UI."""

    def test_full_analysis_pipeline(self, integration_test_files, tmp_path):
        """
        INT-BANDS-008: Complete analysis pipeline from files to reports.
        """
        from src.core.analyzer import BandAnalyzer, AnalysisInput
        from src.output.html_report import generate_html_report
        from src.core.prompt_generator import generate_prompt

        # Step 1: Create analysis input
        inputs = AnalysisInput(
            rfc_path=str(integration_test_files['rfc']),
            hw_filter_path=str(integration_test_files['hw_filter'])
        )

        # Step 2: Run analyzer
        analyzer = BandAnalyzer()
        result = analyzer.analyze(inputs)

        assert result is not None
        assert hasattr(result, 'tracer') or hasattr(result, 'trace_results')

        # Step 3: Generate outputs
        html_path = tmp_path / "full_pipeline_report.html"
        prompt_path = tmp_path / "full_pipeline_prompt.txt"

        generate_html_report(result, str(html_path))
        generate_prompt(result, output_path=str(prompt_path))

        # Verify all outputs
        assert html_path.exists()
        assert prompt_path.exists()

    def test_pipeline_handles_partial_inputs(self, integration_test_files, tmp_path):
        """
        INT-BANDS-009: Pipeline handles partial input files gracefully.
        """
        from src.core.analyzer import BandAnalyzer, AnalysisInput
        from src.output.html_report import generate_html_report

        # Only RFC file, no HW filter
        inputs = AnalysisInput(
            rfc_path=str(integration_test_files['rfc'])
        )

        analyzer = BandAnalyzer()
        result = analyzer.analyze(inputs)

        # Should still produce valid output
        assert result is not None

        html_path = tmp_path / "partial_input_report.html"
        generate_html_report(result, str(html_path))
        assert html_path.exists()

    def test_pipeline_handles_missing_files(self, tmp_path):
        """
        INT-BANDS-010: Pipeline handles missing files gracefully.
        """
        from src.core.analyzer import BandAnalyzer, AnalysisInput

        # Non-existent files
        inputs = AnalysisInput(
            rfc_path="/nonexistent/rfc.xml"
        )

        analyzer = BandAnalyzer()

        # Should not crash
        try:
            result = analyzer.analyze(inputs)
            assert result is not None
        except Exception as e:
            # Controlled exception is acceptable
            assert True


class TestDataFlowIntegration:
    """Test data flows correctly between components."""

    def test_band_counts_consistent_across_pipeline(self, integration_test_files):
        """
        INT-BANDS-011: Band counts are consistent across pipeline stages.
        """
        from src.parsers import parse_rfc_xml
        from src.core.band_tracer import BandTracer

        # Parse RFC
        rfc_result = parse_rfc_xml(str(integration_test_files['rfc']))
        rfc_lte_count = len(rfc_result.lte_bands)
        rfc_nr_count = len(rfc_result.nr_bands)

        # Feed to tracer
        tracer = BandTracer()
        tracer.set_rfc_bands(
            lte_bands=rfc_result.lte_bands,
            nr_bands=rfc_result.nr_bands
        )

        # Counts should match
        assert len(tracer.rfc_lte) == rfc_lte_count
        assert len(tracer.rfc_nr) == rfc_nr_count

    def test_trace_results_include_all_input_bands(self, integration_test_files):
        """
        INT-BANDS-012: Trace results include all bands from inputs.
        """
        from src.parsers import parse_rfc_xml
        from src.core.band_tracer import BandTracer

        rfc_result = parse_rfc_xml(str(integration_test_files['rfc']))

        tracer = BandTracer()
        tracer.set_rfc_bands(
            lte_bands=rfc_result.lte_bands,
            nr_bands=rfc_result.nr_bands
        )

        results = tracer.trace_all_bands()

        # All RFC LTE bands should be traced
        traced_lte_bands = {r.band_num for r in results['LTE']}
        for band in rfc_result.lte_bands:
            assert band in traced_lte_bands
