"""Implementation of TestMonitorClient."""
# Python Modules.
from typing import List, Optional, Union

# Third party modules.
from nisystemlink.clients import core
from nisystemlink.clients.core._uplink._base_client import BaseClient
from nisystemlink.clients.core._uplink._methods import delete, get, post
from nisystemlink.clients.testmonitor import models
from uplink import Query, Body, Path


class TestMonitorClient(BaseClient):
    """Class contains a set of methods to access the APIs of TestMonitor."""

    def __init__(self, configuration: Optional[core.HttpConfiguration] = None):
        """Initialize an instance.

        Args:
            configuration: Defines the web server to connect to and information about
                how to connect. If not provided, an instance of
                :class:`JupyterHttpConfiguration <nisystemlink.clients.core.JupyterHttpConfiguration>`
                is used.

        Raises:
            ApiException: if unable to communicate with the TestMonitor Service.
        """
        if configuration is None:
            configuration = core.JupyterHttpConfiguration()

        super().__init__(configuration, "/nitestmonitor/v2/")

    # paths
    @post("query-steps")
    def query_steps(self, query_filter: models.StepsAdvancedQuery) -> models.StepsQueryResponse:
        """Get a set of steps based on the queryFilter.

        Args:
            query_filter: The filter to be applied when querying for steps.

        Returns:
            The list of steps.
        """
        ...

    @get("steps", args=[Query, Query, Query])
    def get_steps(
        self,
        continuationToken: Union[str, None],
        take: Union[int, None],
        returnCount: bool,
    ) -> models.StepsQueryResponse:
        """Get steps details of multiple steps.

        Args:
            continuationToken: The token used to paginate results.
            take: Limits the returned list of steps to the specified number
            returnCount: Total count of the steps available.

        Returns:
            The list of steps.
        """
        ...

    @post("steps")
    def create_steps(
        self,
        request_body: models.TestStepCreateOrUpdateRequestObject,
    ) -> models.CreateOrUpdateStepsResponse:
        """Create a new steps with the provided steps details.

        Args:
            steps: The request to create the steps.

        Returns:
            The steps details of the newly created steps.
        """
        ...

    @get("results/{resultId}/steps/{stepId}", args=[Path, Path])
    def get_step(self, resultId: str, stepId: Union[str, int]) -> models.TestStepResponseObject:
        """Retrieves the steps details single step identified by stepId and resultId.

        Args:
            resultId: Unique ID of a result.
            stepId: Unique ID of step

        Returns:
            The details of the steps.
        """
        ...

    @delete("results/{resultId}/steps/{stepId}", args=[Path, Path, Query])
    def delete_step(
        self,
        resultId: str,
        stepId: Union[str,int],
        updateResultTotalTime: bool,
    ) -> None:
        """Delete a step with the stepId.

        Args:
            resultId: The id of the result.
            stepId: The id of the step be deleted.


        Returns:
            None
        """
        ...

    @post("query-step-values")
    def query_step_values(self, step_query: models.StepValuesQuery) -> List[str]:
        """Get step values or fields using the step_query.

        Args:
            step_query: The fields to be queried based on filter.

        Returns:
            The list of values based on the step_query.
        """
        ...

    @post("update-steps")
    def update_steps(
        self,
        request_body: models.TestStepCreateOrUpdateRequestObject,
    ) -> models.CreateOrUpdateStepsResponse:
        """Update a set of steps.

        Args:
            request_body: The steps details to be updated with.

        Returns:
            The updated steps response.
        """
        ...

    @post("delete-steps", args=[Body, Query])
    def delete_steps(
        self,
        request_body: models.TestStepsDeleteRequest,
        UpdateResultTotalTime: bool,
    ) -> None:
        """Delete set of steps using the list of steps ids given in the request body.

        Args:
            request_body: The list of pairs of result and step ids to be deleted.

        Returns:
            None
        """
        ...


# print(TestMonitorClient().create_steps(
#     request_body=models.TestStepCreateOrUpdateRequestObject(
#         steps=[
#             models.TestStepRequestObject(
#                 step_id='eigth step',
#                 parentId='root',
#                 children=[
#                     models.TestStepRequestObject(
#                         stepId='child 1',
#                     )
#                 ],
#                 resultId="fb293950-2f0e-45f8-8776-acd5c2ab8252",
#                 has_children=True,
#             )
#         ],
#         update_result_total_time=False
#     )
# ))

# print(TestMonitorClient().get_step(
#     resultId="fb293950-2f0e-45f8-8776-acd5c2ab8252",
#     stepId="Fifth step"
# ))

# print(len(TestMonitorClient().get_steps(
#     continuationToken=None,
#     take=1,
#     returnCount=True
# ).steps))
# print(10*'*')

# print(TestMonitorClient().delete_steps(
#     models.TestStepsDeleteRequest(
#         steps=[models.StepIdResultIdPair(
#             stepId='Step1',
#             resultId='45cba0ec-ebfe-4129-a918-8a5c3d01010f'
#         )]
#     ),
#     UpdateResultTotalTime=False
# ))

# print(TestMonitorClient().delete_step(
#     resultId="45cba0ec-ebfe-4129-a918-8a5c3d01010f",
#     stepId="Step1",
#     updateResultTotalTime=False
# ))

# print(TestMonitorClient().query_steps(
#     query_filter=models.StepsAdvancedQuery(
#         filter="stepId == @0",
#         substitutions=["Step1"],
#     )
# ))

print(TestMonitorClient().update_steps(
    request_body=models.TestStepCreateOrUpdateRequestObject(
        steps=[
            models.TestStepRequestObject(
                stepId='Step1',
                name='Its step',
                status=models.StatusObject(
                    statusType=models.StatusType.PASSED,
                    statusName="Passed",
                )
            )
        ],
        updateResultTotalTime=False
    )
))