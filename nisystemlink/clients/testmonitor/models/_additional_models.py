"""This file contains additional models for Steps APIs."""
# Python modules
from typing import List, Optional, Any, Union

# Third party modules
from  nisystemlink.clients.core._uplink._json_model import JsonModel
from pydantic import Field
from ._testmonitor_models import TestStepResponseObject, TestStepRequestObject, Error


class StepsQueryResponse(JsonModel):
    steps: List[TestStepResponseObject]
    continuation_token: Optional[str] = Field(None, alias="continuationToken")
    total_count: Optional[int] = Field(None, alias="totalCount")


class CreateOrUpdateStepsResponse(JsonModel):
    steps: List[TestStepResponseObject]
    failed: Optional[List[TestStepRequestObject]]
    error: Optional[Error]
