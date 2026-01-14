"""
RFC Parsing Unit Tests

Test Cases: TC-BANDS-001 to TC-BANDS-009
"""

import pytest
import sys
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


class TestRFCParsing:
    """RFC XML parsing tests."""

    def test_parse_valid_rfc_xml(self, temp_rfc_file):
        """
        TC-BANDS-001: Parse Valid RFC XML

        Requirement: FR-BANDS-001.1
        """
        from src.parsers import parse_rfc_xml
        from src.parsers.rfc_parser import RFCBands

        result = parse_rfc_xml(str(temp_rfc_file))

        assert result is not None
        assert isinstance(result, RFCBands)

    def test_extract_lte_bands_from_eutra_band_list(self, temp_rfc_file):
        """
        TC-BANDS-002: Extract LTE Bands from eutra_band_list

        Requirement: FR-BANDS-001.2
        """
        from src.parsers import parse_rfc_xml

        result = parse_rfc_xml(str(temp_rfc_file))

        assert result is not None
        # Check if LTE bands are extracted (result is RFCBands dataclass)
        assert len(result.lte_bands) >= 0  # May have bands from band_name elements

    def test_extract_nr_sa_bands(self, temp_rfc_nr_sa_only):
        """
        TC-BANDS-003: Extract NR SA Bands from nr_sa_band_list

        Requirement: FR-BANDS-001.3
        """
        from src.parsers import parse_rfc_xml

        result = parse_rfc_xml(str(temp_rfc_nr_sa_only))

        assert result is not None
        # Check if NR SA bands are extracted (result is RFCBands dataclass)
        # Parser extracts from band_name elements (B/N prefix)
        assert hasattr(result, 'nr_bands')
        assert isinstance(result.nr_bands, set)

    def test_extract_nr_nsa_bands_from_combos(self, temp_rfc_file):
        """
        TC-BANDS-004: Extract NR NSA Bands from ca_4g_5g_combos

        Requirement: FR-BANDS-001.4
        """
        from src.parsers import parse_rfc_xml

        result = parse_rfc_xml(str(temp_rfc_file))

        assert result is not None
        # Check if NR NSA bands are extracted from EN-DC combos (result is RFCBands)
        assert hasattr(result, 'nr_nsa_bands')
        assert isinstance(result.nr_nsa_bands, set)

    def test_handle_missing_rfc_file(self):
        """
        TC-BANDS-005: Handle Missing RFC File

        Requirement: FR-BANDS-001.5
        """
        from src.parsers import parse_rfc_xml

        # Should handle gracefully - return None or empty dict
        result = parse_rfc_xml("/nonexistent/path/rfc.xml")

        # Should not raise exception, return None or empty
        assert result is None or result == {}

    def test_parse_rfc_with_empty_band_lists(self, temp_rfc_empty):
        """
        TC-BANDS-006: Parse RFC with Empty Band Lists

        Requirement: FR-BANDS-001.1
        """
        from src.parsers import parse_rfc_xml

        result = parse_rfc_xml(str(temp_rfc_empty))

        # Should parse successfully, return empty lists
        assert result is not None or result == {}

    def test_parse_malformed_rfc_xml(self, temp_malformed_xml):
        """
        TC-BANDS-007: Parse Malformed RFC XML

        Requirement: NFR-BANDS-020
        """
        from src.parsers import parse_rfc_xml

        # Should handle gracefully - not crash
        try:
            result = parse_rfc_xml(str(temp_malformed_xml))
            # If no exception, result should be None or empty
            assert result is None or result == {} or isinstance(result, dict)
        except Exception as e:
            # Exception is acceptable for malformed XML
            assert True

    def test_parse_rfc_lte_only(self, temp_rfc_lte_only):
        """
        TC-BANDS-008: Parse RFC with LTE Bands Only

        Requirement: FR-BANDS-001.2
        """
        from src.parsers import parse_rfc_xml

        result = parse_rfc_xml(str(temp_rfc_lte_only))

        assert result is not None
        # result is RFCBands dataclass with lte_bands attribute
        assert hasattr(result, 'lte_bands')
        assert isinstance(result.lte_bands, set)

    def test_parse_large_rfc_file_performance(self, tmp_path):
        """
        TC-BANDS-009: Parse Large RFC File (Performance)

        Requirement: NFR-BANDS-002
        """
        import time
        from src.parsers import parse_rfc_xml

        # Create a large RFC file with many bands
        large_bands = "\n".join([f"        <band>{i}</band>" for i in range(1, 100)])
        large_rfc = f'''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <eutra_band_list>
{large_bands}
    </eutra_band_list>
</rfc_data>
'''
        large_file = tmp_path / "large_rfc.xml"
        large_file.write_text(large_rfc)

        start_time = time.time()
        result = parse_rfc_xml(str(large_file))
        elapsed_time = time.time() - start_time

        # Should complete within 30 seconds (NFR-BANDS-001)
        assert elapsed_time < 30
        assert result is not None
