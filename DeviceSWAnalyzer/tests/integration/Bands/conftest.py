"""
Pytest fixtures for Bands module integration tests.
"""

import pytest
import sys
from pathlib import Path

# Add source to path
base_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))


# =============================================================================
# Sample XML Files for Integration Testing
# =============================================================================

@pytest.fixture
def sample_rfc_xml():
    """Valid RFC XML with multiple band types."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rfc_data>
    <card_properties>
        <hwid>0x1234</hwid>
        <name>Test_RFC_Card</name>
    </card_properties>
    <band_name>B1</band_name>
    <band_name>B3</band_name>
    <band_name>B7</band_name>
    <band_name>B20</band_name>
    <band_name>N77</band_name>
    <band_name>N78</band_name>
    <band_name>N79</band_name>
    <ca_4g_5g_combos>
        <ca_combo>B1A[4];A[1]+N78A[100x4]</ca_combo>
        <ca_combo>B3A[4];A[1]+N77A[100x4]</ca_combo>
    </ca_4g_5g_combos>
</rfc_data>
'''


@pytest.fixture
def sample_hw_filter_xml():
    """HW filter allowing specific bands."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<hardware_band_filtering>
    <gw_bands>0-10</gw_bands>
    <tds_bands></tds_bands>
    <lte_bands>0-6 19-20</lte_bands>
    <nr5g_sa_bands>76-78</nr5g_sa_bands>
    <nr5g_nsa_bands>76-78</nr5g_nsa_bands>
</hardware_band_filtering>
'''


@pytest.fixture
def sample_carrier_policy_xml():
    """Carrier policy with exclusions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<carrier_policy>
    <carrier name="TestCarrier">
        <lte_bands_excluded>20</lte_bands_excluded>
        <nr_sa_bands_excluded>79</nr_sa_bands_excluded>
    </carrier>
</carrier_policy>
'''


@pytest.fixture
def integration_test_files(tmp_path, sample_rfc_xml, sample_hw_filter_xml, sample_carrier_policy_xml):
    """Create all test files for integration testing."""
    files = {}

    # RFC file
    rfc_file = tmp_path / "rfc.xml"
    rfc_file.write_text(sample_rfc_xml)
    files['rfc'] = rfc_file

    # HW Filter file
    hw_file = tmp_path / "hw_filter.xml"
    hw_file.write_text(sample_hw_filter_xml)
    files['hw_filter'] = hw_file

    # Carrier Policy file
    carrier_file = tmp_path / "carrier_policy.xml"
    carrier_file.write_text(sample_carrier_policy_xml)
    files['carrier_policy'] = carrier_file

    return files
