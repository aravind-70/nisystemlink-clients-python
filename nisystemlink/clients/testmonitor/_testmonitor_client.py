"""Implementation of TestMonitorClient."""
from typing import List, Optional, Union

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

    # results
    @post("results")
    def create_results(
        self,
        requestBody: models.CreateTestResultsRequest,
    ) -> models.PartialSuccessOrCompleteSuccess:
        ...

    # steps
    @post("query-steps")
    def query_steps(self, query_filter: models.StepsAdvancedQuery) -> models.StepsQueryResponse:
        """Get a set of steps based on the query_filter.

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
        """Create steps.

        Args:
            request_body: Steps details.

        Returns:
            Created steps details.
        """
        ...

    @get("results/{resultId}/steps/{stepId}", args=[Path, Path])
    def get_step(
        self,
        resultId: str,
        stepId: Union[str, int],
    ) -> models.TestStepResponseObject:
        """Retrieve the details of a single step.

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
        stepId: Optional[str],
        updateResultTotalTime: bool,
    ) -> None:
        """Delete a step.

        Args:
            resultId: Id of the result.
            stepId: Id of the step to be deleted.


        Returns:
            None
        """
        ...

    @post("query-step-values")
    def query_step_values(self, step_query: models.StepValuesQuery) -> List[str]:
        """Get step values or fields.

        Args:
            step_query: The fields to be queried.

        Returns:
            The list of values.
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
    ) -> Union[None, models.DeleteStepsPartialSuccess]:
        """Delete set of steps.

        Args:
            request_body: List of pairs of result ids and step ids to be deleted.

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

    # print(
    #     TestMonitorClient().update_steps(
    #         request_body=models.TestStepCreateOrUpdateRequestObject(
    #             steps=[
    #                 models.TestStepRequestObject(
    #                     stepId="Step1",
    #                     parentId="root",
    #                     resultId="45cba0ec-ebfe-4129-a918-8a5c3d01010f",
    #                     children=[],
    #                     dataModel="TestStand",
    #                     name="My Step",
    #                     status=models.StatusObject(
    #                         statusType=models.StatusType.PASSED, statusName="Passed"
    #                     ),
    #                     stepType="NumericLimitTest",
    #                     totalTimeInSeconds=29.9,
    #                 )
    #             ],
    #             updateResultTotalTime=False,
    #         )
    #     )
    # )


# response = TestMonitorClient().query_step_values(
#     step_query=models.StepValuesQuery(
#         field=models.StepValuesQueryField.STEP_ID,
#         filter="stepId == @0",
#         substitutions=["Step1"],
#         startsWith="Ste",
#     )
# )
# # print(response)
