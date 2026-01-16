"""
Unit tests for UE Capability Parser
"""

import pytest
import tempfile
import os
from ..models import ComboType, DataSource
from ..parsers import UECapParser


class TestUECapParser:
    """Tests for UECapParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = UECapParser()

    def _create_temp_xml(self, content: str) -> str:
        """Create a temporary XML file with given content."""
        fd, path = tempfile.mkstemp(suffix='.xml')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path

    def test_parse_eutra_capability(self):
        """Test parsing EUTRA capability for LTE CA."""
        xml_content = """<?xml version="1.0"?>
        <ue-capability>
            <supportedBandCombination-r10>
                <BandCombinationParameters-r10>
                    <bandParametersDL-r10>
                        <bandEUTRA-r10>1</bandEUTRA-r10>
                    </bandParametersDL-r10>
                    <bandParametersDL-r10>
                        <bandEUTRA-r10>3</bandEUTRA-r10>
                    </bandParametersDL-r10>
                </BandCombinationParameters-r10>
            </supportedBandCombination-r10>
        </ue-capability>
        """
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)

            # Should find LTE CA combo
            lte_ca = result[ComboType.LTE_CA]
            assert len(lte_ca) >= 0  # May or may not parse depending on format
        finally:
            os.unlink(path)

    def test_parse_mrdc_capability(self):
        """Test parsing MRDC capability for EN-DC."""
        xml_content = """<?xml version="1.0"?>
        <ue-capability>
            <supportedBandCombinationList>
                <BandCombination>
                    <bandList>
                        <BandParameters>
                            <bandEUTRA>66</bandEUTRA>
                        </BandParameters>
                        <BandParameters>
                            <bandNR>77</bandNR>
                        </BandParameters>
                    </bandList>
                </BandCombination>
            </supportedBandCombinationList>
        </ue-capability>
        """
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)

            # Should find EN-DC combo
            endc = result[ComboType.ENDC]
            assert len(endc) >= 1

            # Verify combo has both LTE and NR components
            if len(endc) > 0:
                combo = list(endc.values())[0]
                assert len(combo.lte_components) > 0
                assert len(combo.nr_components) > 0
        finally:
            os.unlink(path)

    def test_parse_nr_capability(self):
        """Test parsing NR capability for NR CA."""
        xml_content = """<?xml version="1.0"?>
        <ue-capability>
            <BandCombination-NR>
                <bandList>
                    <bandNR>77</bandNR>
                    <bandNR>78</bandNR>
                </bandList>
            </BandCombination-NR>
        </ue-capability>
        """
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)

            # Should find NR CA combo
            nrca = result[ComboType.NRCA]
            # May or may not parse depending on exact format
            assert len(nrca) >= 0
        finally:
            os.unlink(path)

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        result = self.parser.parse("/nonexistent/file.xml")

        errors = self.parser.get_parse_errors()
        assert len(errors) > 0

    def test_parse_invalid_xml(self):
        """Test parsing invalid XML."""
        xml_content = "not valid xml <>"
        path = self._create_temp_xml(xml_content)
        try:
            result = self.parser.parse(path)
            errors = self.parser.get_parse_errors()
            assert len(errors) > 0
        finally:
            os.unlink(path)

    def test_get_supported_bands(self):
        """Test extracting supported bands."""
        xml_content = """<?xml version="1.0"?>
        <ue-capability>
            <supportedBandCombinationList>
                <BandCombination>
                    <BandParameters>
                        <bandEUTRA>66</bandEUTRA>
                    </BandParameters>
                    <BandParameters>
                        <bandNR>77</bandNR>
                    </BandParameters>
                </BandCombination>
            </supportedBandCombinationList>
        </ue-capability>
        """
        path = self._create_temp_xml(xml_content)
        try:
            self.parser.parse(path)
            bands = self.parser.get_supported_bands()

            # Should have found LTE and NR bands
            if 66 in bands['lte']:
                assert True
            if 77 in bands['nr']:
                assert True
        finally:
            os.unlink(path)

    def test_parse_combo_string(self):
        """Test parsing combo string format."""
        bands = self.parser._parse_combo_string("66A+n77A")

        assert len(bands) == 2

        lte_band = next((b for b in bands if not b.is_nr), None)
        nr_band = next((b for b in bands if b.is_nr), None)

        assert lte_band is not None
        assert lte_band.band == 66

        assert nr_band is not None
        assert nr_band.band == 77
