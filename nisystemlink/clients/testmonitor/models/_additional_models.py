"""This file contains additional models for Steps APIs."""
# Python modules
from typing import List, Optional

from pydantic import Field

from nisystemlink.clients.core._uplink._json_model import JsonModel

from ._testmonitor_models import (
    Error,
    TestResultRequestObject,
    TestResultResponseObject,
    TestStepRequestObject,
    TestStepResponseObject,
    StepIdResultIdPair,
)


class CreateTestResultsRequest(JsonModel):
    results: List[TestResultRequestObject]


class CreateResultPartialSuccessResponse(JsonModel):
    results: List[TestResultResponseObject]
    """
    Array of created results.
    """
    failed: Optional[List[TestResultRequestObject]]
    """
    Array of failed results.
    """
    error: Optional[Error]
    """
    Default error model.
    """


class StepsQueryResponse(JsonModel):
    steps: List[TestStepResponseObject]
    continuation_token: Optional[str] = Field(None, alias="continuationToken")
    total_count: Optional[int] = Field(None, alias="totalCount")


class CreateOrUpdateStepsResponse(JsonModel):
    steps: List[TestStepResponseObject]
    failed: Optional[List[TestStepRequestObject]]
    error: Optional[Error]


class DeleteStepsPartialSuccess(JsonModel):
    steps: List[StepIdResultIdPair]
    failed: Optional[List[StepIdResultIdPair]]
    error: Optional[Error]


class QueryStepsValuesResponse(JsonModel):
    __root__: List[str]
