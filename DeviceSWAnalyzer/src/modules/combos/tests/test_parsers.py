"""
Unit tests for RFC and QXDM Parsers
"""

import pytest
import tempfile
import os
from ..models import ComboType, DataSource
from ..parsers import RFCParser, QXDMParser


class TestRFCParser:
    """Tests for RFCParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RFCParser()

    def _create_temp_xml(self, content: str) -> str:
        """Create a temporary XML file with given content."""
        fd, path = tempfile.mkstemp(suffix='.xml')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path

    def test_parse_lte_ca_combos(self):
        """Test parsing LTE CA combos from RFC XML."""
        xml_content = """<?xml version="1.0"?>
        <rfc>
            <ca_combos>
                <ca_combo>B1A[4];A[1]+B3A[4];A[1]</ca_combo>
                <ca_combo>B7A[4];A[1]</ca_combo>
            </ca_combos>
        </rfc>
        """
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)

            assert ComboType.LTE_CA in result
            lte_ca = result[ComboType.LTE_CA]
            assert len(lte_ca) == 2
            assert '1A-3A' in lte_ca.keys() or '3A-1A' in lte_ca.keys()
        finally:
            os.unlink(path)

    def test_parse_endc_combos(self):
        """Test parsing EN-DC combos from RFC XML."""
        xml_content = """<?xml version="1.0"?>
        <rfc>
            <ca_4g_5g_combos>
                <ca_combo>B66A[4];A[1]+N77A[100x4];A[100x1]</ca_combo>
            </ca_4g_5g_combos>
        </rfc>
        """
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)

            assert ComboType.ENDC in result
            endc = result[ComboType.ENDC]
            assert len(endc) >= 1

            # Should have both LTE and NR components
            combo = list(endc.values())[0]
            assert len(combo.lte_components) > 0
            assert len(combo.nr_components) > 0
        finally:
            os.unlink(path)

    def test_parse_band_entry_simple(self):
        """Test parsing simple band entry."""
        result = self.parser._parse_band_entry("B66A")

        assert result is not None
        assert result.band == 66
        assert result.band_class == 'A'
        assert result.is_nr is False

    def test_parse_band_entry_with_mimo(self):
        """Test parsing band entry with MIMO info."""
        result = self.parser._parse_band_entry("B66A[4]")

        assert result is not None
        assert result.band == 66
        assert result.band_class == 'A'
        assert result.mimo_layers == 4

    def test_parse_band_entry_nr(self):
        """Test parsing NR band entry."""
        result = self.parser._parse_band_entry("N77A[100x4]")

        assert result is not None
        assert result.band == 77
        assert result.band_class == 'A'
        assert result.is_nr is True
        assert result.mimo_layers == 4

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        result = self.parser.parse("/nonexistent/file.xml")

        errors = self.parser.get_parse_errors()
        assert len(errors) > 0
        assert "not found" in errors[0].lower() or "file" in errors[0].lower()

    def test_parse_invalid_xml(self):
        """Test parsing invalid XML content."""
        xml_content = "this is not valid xml <>"
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)
            errors = self.parser.get_parse_errors()
            assert len(errors) > 0
        finally:
            os.unlink(path)

    def test_skip_nr_combos_in_lte_ca_section(self):
        """Test that NR combos in ca_combos section are skipped."""
        xml_content = """<?xml version="1.0"?>
        <rfc>
            <ca_combos>
                <ca_combo>B1A[4]+B3A[4]</ca_combo>
                <ca_combo>B66A[4]+N77A[4]</ca_combo>
            </ca_combos>
        </rfc>
        """
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)

            lte_ca = result[ComboType.LTE_CA]
            # The combo with N77 should be skipped from LTE_CA
            for combo in lte_ca.values():
                assert len(combo.nr_components) == 0
        finally:
            os.unlink(path)


class TestQXDMParser:
    """Tests for QXDMParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QXDMParser()

    def _create_temp_txt(self, content: str) -> str:
        """Create a temporary text file with given content."""
        fd, path = tempfile.mkstemp(suffix='.txt')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path

    def test_parse_structured_format(self):
        """Test parsing structured QXDM format."""
        content = """
        Combo Index = 0
        Number of Bands = 2
        [Band 0]
        RAT Type = LTE
        Band = 66
        DL BW Class = A
        UL BW Class = A
        DL MIMO = 4
        [Band 1]
        RAT Type = NR
        Band = 77
        DL BW Class = A
        """
        path = self._create_temp_txt(content)
        try:
            result = self.parser.parse(path)

            # Should find EN-DC combo
            endc = result[ComboType.ENDC]
            assert len(endc) >= 1
        finally:
            os.unlink(path)

    def test_parse_table_format(self):
        """Test parsing table format."""
        content = """
        Index | RAT  | Band | DL BW | UL BW | DL MIMO | UL MIMO
        ------|------|------|-------|-------|---------|--------
          0   | LTE  |  66  |   A   |   A   |    4    |    1
          0   | NR   |  77  |   A   |   A   |    4    |    1
          1   | LTE  |   2  |   A   |   A   |    4    |    1
        """
        path = self._create_temp_txt(content)
        try:
            result = self.parser.parse(path)

            # Should find combos
            total = sum(len(combo_set) for combo_set in result.values())
            assert total >= 1
        finally:
            os.unlink(path)

    def test_parse_raw_format_dc_notation(self):
        """Test parsing DC_xxA_nyyA format."""
        content = """
        DC_66A_n77A
        DC_2A_n71A
        """
        path = self._create_temp_txt(content)
        try:
            result = self.parser.parse(path)

            endc = result[ComboType.ENDC]
            assert len(endc) >= 1
        finally:
            os.unlink(path)

    def test_parse_labeled_combos(self):
        """Test parsing labeled combo format."""
        content = """
        ENDC: B66A+N77A
        LTE-CA: B1A+B3A+B7A
        """
        path = self._create_temp_txt(content)
        try:
            result = self.parser.parse(path)

            total = sum(len(combo_set) for combo_set in result.values())
            assert total >= 1
        finally:
            os.unlink(path)

    def test_extract_bands_from_string(self):
        """Test band extraction from combo string."""
        bands = self.parser._extract_bands_from_string("B66A+N77A")

        assert len(bands) == 2

        lte_band = next((b for b in bands if not b.get('rat') == 'NR'), None)
        nr_band = next((b for b in bands if b.get('rat') == 'NR'), None)

        assert lte_band is not None
        assert lte_band['band'] == 66

        assert nr_band is not None
        assert nr_band['band'] == 77

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        result = self.parser.parse("/nonexistent/file.txt")

        errors = self.parser.get_parse_errors()
        assert len(errors) > 0

    def test_parse_empty_file(self):
        """Test parsing empty file."""
        content = ""
        path = self._create_temp_txt(content)
        try:
            result = self.parser.parse(path)

            total = sum(len(combo_set) for combo_set in result.values())
            assert total == 0

            errors = self.parser.get_parse_errors()
            assert len(errors) > 0  # Should report parsing failure
        finally:
            os.unlink(path)

    def test_combo_type_detection(self):
        """Test correct combo type detection."""
        content = """
        Combo Index = 0
        [Band 0]
        RAT Type = LTE
        Band = 1
        DL BW Class = A
        [Band 1]
        RAT Type = LTE
        Band = 3
        DL BW Class = A

        Combo Index = 1
        [Band 0]
        RAT Type = LTE
        Band = 66
        DL BW Class = A
        [Band 1]
        RAT Type = NR
        Band = 77
        DL BW Class = A
        """
        path = self._create_temp_txt(content)
        try:
            result = self.parser.parse(path)

            # Should have both LTE CA and EN-DC
            assert len(result[ComboType.LTE_CA]) >= 1
            assert len(result[ComboType.ENDC]) >= 1
        finally:
            os.unlink(path)

    def test_get_combo_count(self):
        """Test combo count tracking."""
        content = """
        Combo Index = 0
        RAT Type = LTE
        Band = 66
        DL BW Class = A

        Combo Index = 1
        RAT Type = NR
        Band = 77
        DL BW Class = A
        """
        path = self._create_temp_txt(content)
        try:
            self.parser.parse(path)

            count = self.parser.get_combo_count()
            assert count >= 2
        finally:
            os.unlink(path)
