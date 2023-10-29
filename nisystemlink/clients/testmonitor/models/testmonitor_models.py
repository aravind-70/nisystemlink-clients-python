"""Contains Custom Models for Product APIs."""

# Python Modules
from typing import List, Optional, Dict

# Relative Modules
from nisystemlink.clients.core._uplink._json_model import JsonModel

from ._test_monitor_models import (
    Operations1,
    ProductRequestObject,
    ProductResponseObject,
    ProductUpdateRequestObject,
    Error
)

class ApiInfo(JsonModel):
    operations: Operations1


class CreateProductsRequest(JsonModel):
    products: List[ProductRequestObject]
    """
    Array of products to be created.
    """


class CreateProductsResponse(JsonModel):
    products: List[ProductResponseObject]
    """
    Array of products which are created.
    """
    failed: Optional[List[ProductRequestObject]]
    """
    Unsuccessful Array of products which are failed.
    """
    error: Optional[Error]
    """
    Default error model.
    """



class ProductsQueryResponse(JsonModel):
    products: List[ProductResponseObject]
    """
    Array of products.
    """
    continuation_token: Optional[str]
    """
    A token which allows the user to resume this query at the next item in the matching product set. In order to continue paginating a query, pass this token to the service on a subsequent request. The service will respond with a new continuation token. To paginate a set of products, continue sending requests with the newest continuation token provided by the service, until this value is null.
    """
    total_count: Optional[str]
    """
    The number of matching products, if returnCount is true. This value is not present if returnCount is false.
    """


class ProductDeleteRequest(JsonModel):
    ids: List[str]
    """
    Array of product ids to delete.
    """


class CreateProductUpdateRequest(JsonModel):
    products: List[ProductUpdateRequestObject]
    """
    Array of products to update.
    """
    replace: str
    """
    Replace the existing fields instead of merging them.
    """


class ProductUpdateResponse(JsonModel):
    products: List[ProductResponseObject]
    """
    Array of products which are updated.
    """
    failed: Optional[List[ProductRequestObject]]
    """
    Failed products which are to be updated.
    """
    error: Optional[Error]
    """
    Default error model.
    """
