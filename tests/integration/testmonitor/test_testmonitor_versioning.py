"""This file contains test function for the versioning API of TestMonitorClient."""
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
    """Class contains a test method to test versioning API of TestMonitor."""

    def test__api_info(self, client: TestMonitorClient):
        """Test the versioning API info."""
        response = client.api_info()
        assert response is not None
