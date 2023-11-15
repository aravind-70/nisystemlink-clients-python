"""This file contains the test class for steps APIs of TestMonitor."""
import pytest
from datetime import datetime, timezone

from nisystemlink.clients.core import ApiException
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
    TestStepsDeleteRequest,
    StepIdResultIdPair,
    StepsAdvancedQuery,
    StepField,
)
from nisystemlink.clients.auth import AuthClient

api_info = AuthClient().get_auth()
if api_info.workspaces:
    workspace_id = api_info.workspaces[0].id

INVALID_ID = "invalid_id"
TOTAL_TIME_IN_SECONDS = 7


@pytest.fixture(scope="class")
def get_step_id():
    step_id = 0

    def _get_step_id():
        nonlocal step_id
        step_id += 1
        return step_id

    yield _get_step_id


@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient object."""
    return TestMonitorClient(enterprise_config)


# Create a test result
@pytest.fixture(scope="class")
def get_result_id(client: TestMonitorClient):
    request_body = CreateTestResultsRequest(
        results=[
            TestResultRequestObject(
                programName="TestResult",
                status=StatusObject(statusType=StatusType.PASSED, statusName="PASSED"),
                workspace=workspace_id,
            )
        ]
    )
    response = client.create_results(request_body)
    result_id = response.results[0].id
    return result_id


@pytest.fixture(scope="class")
def create_steps_request_body(client: TestMonitorClient, get_result_id, get_step_id):
    def _create_steps_request_body():
        step_num = str(get_step_id())
        request_body = TestStepCreateOrUpdateRequestObject(
            steps=[
                TestStepRequestObject(
                    step_id=step_num,
                    parent_id="root",
                    result_id=get_result_id,
                    data=StepDataObject(
                        text="Outputs",
                        parameters=[
                            {
                                "name": "voltage",
                                "status": "Passed",
                                "lowLimit": "1.1",
                                "highLimit": "2.2",
                                "unit": "volt",
                            }
                        ],
                    ),
                    data_model="TestModel",
                    name=f"TestStep_{step_num}",
                    started_at=datetime.now(),
                    step_type="Test",
                    total_time_in_seconds=TOTAL_TIME_IN_SECONDS,
                    inputs=[NamedValueObject(name="voltage", value=1.5)],
                    outputs=[NamedValueObject(name="current", value=2.5)],
                )
            ],
            updateResultTotalTime=True,
        )
        return request_body

    yield _create_steps_request_body


@pytest.fixture(scope="class")
def test_steps(client: TestMonitorClient, create_steps_request_body):
    steps = []

    for _ in range(4):
        request_body = create_steps_request_body()
        response = client.create_steps(request_body=request_body)
        steps.append(response.steps[0])

    return steps


@pytest.mark.integration
@pytest.mark.enterprise
class TestSuiteTestMonitorClientSteps:
    def test__create_steps__complete_success(
        self,
        client: TestMonitorClient,
        create_steps_request_body,
    ):
        request_body = create_steps_request_body()
        response = client.create_steps(request_body=request_body)

        assert response.failed is None
        assert response.error is None
        assert response.steps is not None
        assert len(response.steps) == 1

    def test__create_steps__partial_success(
        self,
        client: TestMonitorClient,
        get_step_id,
        get_result_id,
    ):
        step_id = get_step_id()
        request_body = TestStepCreateOrUpdateRequestObject(
            steps=[
                TestStepRequestObject(
                    step_id=str(step_id),
                    result_id=get_result_id,
                ),
                TestStepRequestObject(  # Duplicate product
                    step_id=str(step_id),
                    result_id=get_result_id,
                ),
            ]
        )

        response = client.create_steps(request_body=request_body)

        assert response.steps is not None
        assert len(response.steps) == 1

        assert response.failed is not None
        assert len(response.failed) == 1

        assert response.error is not None

    def test__get_step(self, client: TestMonitorClient, get_result_id, test_steps):
        result_id = get_result_id
        test_step = test_steps[0]
        step_details = client.get_step(resultId=result_id, stepId=test_step.step_id)

        assert step_details.step_id == test_step.step_id
        assert step_details.parent_id == test_step.parent_id
        assert step_details.result_id == test_step.result_id

    def test__get_step__invalid_id(self, client: TestMonitorClient):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_step(resultId=INVALID_ID, stepId=INVALID_ID)

    def test__get_steps__without_total_count(self, client: TestMonitorClient):
        take = 1
        response = client.get_steps(continuationToken=None, take=take, returnCount=False)

        assert response.total_count is None
        assert len(response.steps) == take

    def test__get_steps__with_total_count(self, client: TestMonitorClient):
        take = 2
        response = client.get_steps(continuationToken=None, take=take, returnCount=True)

        assert response.total_count is not None
        assert response.total_count > 0
        assert len(response.steps) == take

    def test__delete_step(
        self,
        client: TestMonitorClient,
        create_steps_request_body,
        get_result_id,
    ):
        request_body = create_steps_request_body()
        created_step = client.create_steps(request_body=request_body)
        step_id = created_step.steps[0].step_id

        deleted_step = client.delete_step(
            resultId=get_result_id,
            stepId=step_id,
            updateResultTotalTime=True,
        )

        assert deleted_step is None

    def test__delete_step__invalid_id(self, client: TestMonitorClient):
        with pytest.raises(ApiException, match="400"):
            client.delete_step(resultId=INVALID_ID, stepId=INVALID_ID, updateResultTotalTime=True)

    def test__delete_steps__complete_success(
        self,
        client: TestMonitorClient,
        create_steps_request_body,
        get_result_id,
    ):
        result_step_pair = []
        for _ in range(3):
            request_body = create_steps_request_body()
            created_step = client.create_steps(request_body=request_body)
            result_step_pair.append(
                StepIdResultIdPair(step_id=created_step.steps[0].step_id, result_id=get_result_id)
            )

        request_body = TestStepsDeleteRequest(steps=result_step_pair)

        response = client.delete_steps(request_body=request_body, UpdateResultTotalTime=False)
        assert response is None

    def test__delete_steps__partial_success(
        self,
        client: TestMonitorClient,
        create_steps_request_body,
        get_result_id,
    ):
        result_step_pair = []
        for _ in range(3):
            request_body = create_steps_request_body()
            created_step = client.create_steps(request_body=request_body)
            result_step_pair.append(
                StepIdResultIdPair(step_id=created_step.steps[0].step_id, result_id=get_result_id)
            )

        result_step_pair.append(
            StepIdResultIdPair(
                step_id=INVALID_ID,
                result_id=INVALID_ID,
            )
        )
        request_body = TestStepsDeleteRequest(steps=result_step_pair)
        response = client.delete_steps(request_body=request_body, UpdateResultTotalTime=False)

        assert response is not None
        assert response.steps is not None
        assert response.failed is not None
        assert response.error is not None

    def test__update_steps__complete_success(
        self, client: TestMonitorClient, test_steps, get_result_id
    ):
        test_step = test_steps[1]
        started_at = datetime.now(timezone.utc)

        request_body = TestStepCreateOrUpdateRequestObject(
            steps=[
                TestStepRequestObject(
                    step_id=test_step.step_id,
                    result_id=get_result_id,
                    started_at=started_at,
                    total_time_in_seconds=TOTAL_TIME_IN_SECONDS + 1,
                )
            ],
            update_result_total_time=True,
        )

        response = client.update_steps(request_body=request_body)

        assert response.failed is None
        assert response.error is None
        assert response.steps is not None

        updated_step = response.steps[0]
        assert updated_step.started_at == started_at
        assert updated_step.total_time_in_seconds == TOTAL_TIME_IN_SECONDS + 1

    def test__update_steps__partial_success(
        self, client: TestMonitorClient, test_steps, get_result_id
    ):
        test_step = test_steps[2]
        started_at = datetime.now(timezone.utc)

        request_body = TestStepCreateOrUpdateRequestObject(
            steps=[
                TestStepRequestObject(
                    step_id=test_step.step_id,
                    result_id=get_result_id,
                    started_at=started_at,
                    total_time_in_seconds=TOTAL_TIME_IN_SECONDS + 1,
                ),
                TestStepRequestObject(step_id=INVALID_ID, result_id=INVALID_ID),
            ],
            update_result_total_time=True,
        )

        response = client.update_steps(request_body=request_body)
        assert response.steps is not None
        assert len(response.steps) == 1

        updated_step = response.steps[0]
        assert updated_step.started_at == started_at
        assert updated_step.total_time_in_seconds == TOTAL_TIME_IN_SECONDS + 1

        assert response.failed is not None
        assert len(response.failed) == 1
        assert response.error is not None

    def test__query_steps(self, client: TestMonitorClient, get_result_id, test_steps):
        query_filter = StepsAdvancedQuery(
            filter="stepId > @0",
            substitutions=[test_steps[3].step_id],
            result_filter="resultId == @0",
            result_substitutions=[get_result_id],
            projection=[StepField.NAME],
            return_count=True
        )
        response = client.query_steps(query_filter=query_filter)
        assert response.steps is not None
        assert len(response.steps) == 1
        assert response.total_count is not None

    # def test__query_step_values(self, client: TestMonitorClient):
