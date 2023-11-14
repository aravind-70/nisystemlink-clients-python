"""This file contains the test class for steps APIs of TestMonitor."""
import pytest

from nisystemlink.clients.testmonitor import TestMonitorClient
from nisystemlink.clients.testmonitor.models import (
    CreateTestResultsRequest,
    TestResultRequestObject,
    StepDataObject,
    NamedValueObject,
    StatusObject,
    StatusType,
    TestStepCreateOrUpdateRequestObject,
    TestStepRequestObject,
)
from nisystemlink.clients.auth import AuthClient

api_info = AuthClient().get_auth()
workspace_id = api_info.workspaces[0].id

@pytest.fixture(scope="class")
def client(enterprise_config) -> TestMonitorClient:
    """Fixture to create a TestMonitorClient object."""
    return TestMonitorClient(enterprise_config)


# Create a test result
request_body = CreateTestResultsRequest(
    results=[
        TestResultRequestObject(
            programName="TestResult",
            status=StatusObject(statusType=StatusType.PASSED, statusName="PASSED"),
            workspace=workspace_id,
        )
    ]
)
response = TestMonitorClient().create_results(request_body)
result_id = response.results[0].id

@pytest.fixture(scope="class")
def create_steps_request_body(client: TestMonitorClient):
    def _create_steps_request_body():
        create_request = TestStepCreateOrUpdateRequestObject(
            steps=[
                TestStepRequestObject(
                    step_id="Test_Step_1",
                    parent_id="root",
                    result_id=result_id,
                )
            ]
        )
        return create_request

    yield _create_steps_request_body


@pytest.fixture(scope="class")
def create_steps(client: TestMonitorClient):
    request_body = create_steps_request_body()
    steps = client.create_steps(request_body=request_body)

class TestSuiteTestMonitorClientSteps:


    def test__create_steps__complete_success(client: TestMonitorClient, create_steps_request_body):
    


    def test__create_steps__partial_success(client: TestMonitorClient, create_steps_request_body):
    


    def test__get_step(client: TestMonitorClient):

    
    def test__get_step__invalid_id(client: TestMonitorClient):


    def test__get_steps(client: TestMonitorClient):
    


    def test__delete_step(client: TestMonitorClient):
    

    def test__delete_step__invalid_id(client: TestMonitorClient):
    

    def test__query_step_values(client: TestMonitorClient):
    

    def test__update_steps__complete_success(client: TestMonitorClient):
    

    def test__update_steps__partial_success(client: TestMonitorClient):
    

    def test__delete_steps(client: TestMonitorClient):
    

    def test__delete_steps__invalid_id(client: TestMonitorClient):
