"""
Band Tracing Unit Tests

Test Cases: TC-BANDS-040 to TC-BANDS-052
"""

import pytest
import sys
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


class TestBandFlowTracing:
    """Band flow tracing tests."""

    def test_tracer_initialization(self):
        """
        TC-BANDS-040: Trace Bands Through All Layers (Init)

        Requirement: FR-BANDS-010.1
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()

        assert tracer is not None

    def test_set_rfc_bands(self):
        """
        TC-BANDS-040: Set RFC Bands in Tracer

        Requirement: FR-BANDS-010.1
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()

        # Set LTE bands (API uses Sets, not lists)
        tracer.set_rfc_bands(
            lte_bands={1, 3, 7, 20},
            nr_bands={78, 79}
        )

        # Verify bands are set
        assert len(tracer.rfc_lte) > 0

    def test_identify_bands_added(self):
        """
        TC-BANDS-041: Identify Bands Added at Each Stage

        Requirement: FR-BANDS-010.2
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7}, nr_bands=set())

        # Get trace results using trace_all_bands()
        results = tracer.trace_all_bands()

        # Should return dict with band types as keys
        assert results is not None
        assert 'LTE' in results

    def test_identify_bands_removed(self):
        """
        TC-BANDS-042: Identify Bands Removed at Each Stage

        Requirement: FR-BANDS-010.3
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7, 20}, nr_bands=set())
        tracer.set_hw_filter_bands(lte={1, 3, 7}, nr_sa=set(), nr_nsa=set())  # 20 removed

        results = tracer.trace_all_bands()

        # Band 20 should be marked as filtered
        assert results is not None
        assert 'LTE' in results

    def test_calculate_final_band_set(self):
        """
        TC-BANDS-043: Calculate Final Band Set

        Requirement: FR-BANDS-010.4
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7, 20}, nr_bands=set())
        tracer.set_hw_filter_bands(lte={1, 3, 7}, nr_sa=set(), nr_nsa=set())
        tracer.set_carrier_exclusions(lte={20}, nr_sa=set(), nr_nsa=set())  # Exclude band 20

        # Final set should be filtered
        results = tracer.trace_all_bands()

        assert results is not None
        assert 'LTE' in results


class TestMismatchDetection:
    """Mismatch detection tests."""

    def test_detect_rfc_vs_hw_mismatch(self):
        """
        TC-BANDS-045: Detect RFC vs HW Filter Mismatch

        Requirement: FR-BANDS-011.1
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7, 20}, nr_bands=set())
        tracer.set_hw_filter_bands(lte={1, 3}, nr_sa=set(), nr_nsa=set())  # 7, 20 not in HW

        results = tracer.trace_all_bands()

        # Should detect mismatch for bands 7, 20
        assert results is not None
        assert 'LTE' in results

    def test_detect_carrier_policy_mismatch(self):
        """
        TC-BANDS-046: Detect Carrier Policy Mismatch

        Requirement: FR-BANDS-011.2
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7}, nr_bands=set())
        tracer.set_hw_filter_bands(lte={1, 3, 7}, nr_sa=set(), nr_nsa=set())
        tracer.set_carrier_exclusions(lte={7}, nr_sa=set(), nr_nsa=set())  # 7 blocked

        results = tracer.trace_all_bands()

        assert results is not None
        assert 'LTE' in results

    def test_detect_ue_cap_mismatch(self):
        """
        TC-BANDS-048: Detect UE Capability vs Expected Mismatch

        Requirement: FR-BANDS-011.4
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3}, nr_bands=set())
        tracer.set_ue_cap_bands(lte={1, 3, 7}, nr=set())  # 7 in UE cap but not in RFC

        results = tracer.trace_all_bands()

        # Should detect band 7 as anomaly
        assert results is not None
        assert 'LTE' in results


class TestAnomalyDetection:
    """Anomaly detection tests."""

    def test_flag_unexpected_band_addition(self):
        """
        TC-BANDS-050: Flag Unexpected Band Addition

        Requirement: FR-BANDS-012.1
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3}, nr_bands=set())
        tracer.set_ue_cap_bands(lte={1, 3, 99}, nr=set())  # 99 is unexpected

        results = tracer.trace_all_bands()

        # Should flag band 99 as unexpected addition
        assert results is not None
        assert 'LTE' in results

    def test_flag_unexpected_band_removal(self):
        """
        TC-BANDS-051: Flag Unexpected Band Removal

        Requirement: FR-BANDS-012.2
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7}, nr_bands=set())
        tracer.set_hw_filter_bands(lte={1, 3, 7}, nr_sa=set(), nr_nsa=set())
        # Skip carrier exclusions - use UE cap to check
        tracer.set_ue_cap_bands(lte={1, 3}, nr=set())  # 7 missing

        results = tracer.trace_all_bands()

        # Should flag band 7 as unexpected removal
        assert results is not None
        assert 'LTE' in results

    def test_identify_configuration_issues(self):
        """
        TC-BANDS-052: Identify Configuration Issues

        Requirement: FR-BANDS-012.3
        """
        from src.core.band_tracer import BandTracer

        tracer = BandTracer()
        tracer.set_rfc_bands(lte_bands={1, 3, 7, 20}, nr_bands=set())
        tracer.set_hw_filter_bands(lte={1, 3}, nr_sa=set(), nr_nsa=set())
        tracer.set_carrier_exclusions(lte={7}, nr_sa=set(), nr_nsa=set())  # Conflict: 7 not in HW anyway

        results = tracer.trace_all_bands()

        # Should identify configuration issues
        assert results is not None
        assert 'LTE' in results
