"""Implementation of TestMonitorClient."""
from typing import Optional, Union

from uplink import Body, Path, Query

from nisystemlink.clients import core
from nisystemlink.clients.core._uplink._base_client import BaseClient
from nisystemlink.clients.core._uplink._methods import delete, get, post
from nisystemlink.clients.testmonitor import models


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
    def query_step_values(
        self, step_query: models.StepValuesQuery
    ) -> models.QueryStepsValuesResponse:
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
