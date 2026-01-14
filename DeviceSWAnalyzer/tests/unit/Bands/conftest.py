"""
Pytest fixtures for Bands module unit tests.
"""

import pytest
import sys
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


# =============================================================================
# Sample XML Content
# =============================================================================

@pytest.fixture
def sample_rfc_xml():
    """Valid RFC XML content with LTE, NR SA, and NR NSA bands."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <gsm_bands>
        <band>850</band>
        <band>900</band>
        <band>1800</band>
        <band>1900</band>
    </gsm_bands>
    <wcdma_bands>
        <band>1</band>
        <band>2</band>
        <band>5</band>
        <band>8</band>
    </wcdma_bands>
    <eutra_band_list>
        <band>1</band>
        <band>3</band>
        <band>7</band>
        <band>20</band>
        <band>38</band>
        <band>40</band>
        <band>41</band>
    </eutra_band_list>
    <nr_sa_band_list>
        <band>n78</band>
        <band>n79</band>
        <band>n77</band>
    </nr_sa_band_list>
    <nr_nsa_combos>
        <combo>
            <lte_band>3</lte_band>
            <nr_band>n78</nr_band>
        </combo>
        <combo>
            <lte_band>7</lte_band>
            <nr_band>n79</nr_band>
        </combo>
    </nr_nsa_combos>
</rfc_data>
'''


@pytest.fixture
def sample_rfc_lte_only_xml():
    """RFC XML with LTE bands only."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <eutra_band_list>
        <band>1</band>
        <band>3</band>
        <band>7</band>
        <band>20</band>
    </eutra_band_list>
</rfc_data>
'''


@pytest.fixture
def sample_rfc_nr_sa_only_xml():
    """RFC XML with NR SA bands only."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <nr_sa_band_list>
        <band>n78</band>
        <band>n79</band>
        <band>n260</band>
        <band>n261</band>
    </nr_sa_band_list>
</rfc_data>
'''


@pytest.fixture
def sample_rfc_empty_xml():
    """RFC XML with empty band lists."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <eutra_band_list>
    </eutra_band_list>
    <nr_sa_band_list>
    </nr_sa_band_list>
</rfc_data>
'''


@pytest.fixture
def malformed_xml():
    """Malformed XML for error handling tests."""
    return '''<?xml version="1.0"?>
<rfc_data>
    <unclosed_tag>
    <band>1</band>
</rfc_data>
'''


@pytest.fixture
def sample_hw_filter_xml():
    """Sample HW filter XML (matches hardware_band_filtering.xml format)."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<hardware_band_filtering>
    <gw_bands>0-10</gw_bands>
    <tds_bands></tds_bands>
    <lte_bands>0-6 19-39</lte_bands>
    <nr5g_sa_bands>0-10 76-78</nr5g_sa_bands>
    <nr5g_nsa_bands>0-10 76-78</nr5g_nsa_bands>
</hardware_band_filtering>
'''


@pytest.fixture
def sample_carrier_policy_xml():
    """Sample carrier policy XML."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<carrier_policy>
    <carrier name="TestCarrier">
        <lte_bands>
            <enabled>
                <band>1</band>
                <band>3</band>
            </enabled>
            <disabled>
                <band>7</band>
            </disabled>
        </lte_bands>
    </carrier>
</carrier_policy>
'''


# =============================================================================
# Temp File Fixtures
# =============================================================================

@pytest.fixture
def temp_rfc_file(tmp_path, sample_rfc_xml):
    """Create temporary RFC XML file."""
    rfc_file = tmp_path / "test_rfc.xml"
    rfc_file.write_text(sample_rfc_xml)
    return rfc_file


@pytest.fixture
def temp_rfc_lte_only(tmp_path, sample_rfc_lte_only_xml):
    """Create temporary RFC XML file with LTE only."""
    rfc_file = tmp_path / "test_rfc_lte.xml"
    rfc_file.write_text(sample_rfc_lte_only_xml)
    return rfc_file


@pytest.fixture
def temp_rfc_nr_sa_only(tmp_path, sample_rfc_nr_sa_only_xml):
    """Create temporary RFC XML file with NR SA only."""
    rfc_file = tmp_path / "test_rfc_nr_sa.xml"
    rfc_file.write_text(sample_rfc_nr_sa_only_xml)
    return rfc_file


@pytest.fixture
def temp_rfc_empty(tmp_path, sample_rfc_empty_xml):
    """Create temporary RFC XML file with empty bands."""
    rfc_file = tmp_path / "test_rfc_empty.xml"
    rfc_file.write_text(sample_rfc_empty_xml)
    return rfc_file


@pytest.fixture
def temp_malformed_xml(tmp_path, malformed_xml):
    """Create temporary malformed XML file."""
    xml_file = tmp_path / "malformed.xml"
    xml_file.write_text(malformed_xml)
    return xml_file


@pytest.fixture
def temp_hw_filter_file(tmp_path, sample_hw_filter_xml):
    """Create temporary HW filter XML file."""
    hw_file = tmp_path / "hw_filter.xml"
    hw_file.write_text(sample_hw_filter_xml)
    return hw_file


@pytest.fixture
def temp_carrier_policy_file(tmp_path, sample_carrier_policy_xml):
    """Create temporary carrier policy XML file."""
    policy_file = tmp_path / "carrier_policy.xml"
    policy_file.write_text(sample_carrier_policy_xml)
    return policy_file
