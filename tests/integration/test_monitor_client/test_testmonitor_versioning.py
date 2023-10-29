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
    """Fixture to create a request body object of create_products API."""

    def test__api_info(self, client):
        response = client.api_info()
        assert len(response.dict()) != 0
