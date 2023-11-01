"""This file contains test functions for the versioning API of TestMonitorClient."""
# Third Party Modules
import pytest
# Relative modules
from nisystemlink.clients.testmonitor import TestMonitorClient
 
 
@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient instance."""
    return TestMonitorClient(enterprise_config)
 
 
@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClientVersioning:
    """Class contains a test methods to test versioning API of TestMonitor."""
 
    def test__api_info(self, client):
        """Test second version of api info."""
        response = client.api_info()
        assert len(response.dict()) != 0