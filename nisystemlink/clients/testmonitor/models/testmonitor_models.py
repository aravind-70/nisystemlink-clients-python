from typing import List

from ._test_monitor_models import (
    ProductRequestObject,
    ProductResponseObject,
    ProductUpdateRequestObject,
    Error,
)
from nisystemlink.clients.core._uplink._json_model import JsonModel


class CreateProductsRequest(JsonModel):
    products: List[ProductRequestObject]


class CreateProductsResponse(JsonModel):
    products: List[ProductResponseObject]


class ProductsQueryResponse(JsonModel):
    products: List[ProductResponseObject]
    continuation_token: str
    total_count: str


class ProductDeleteRequest(JsonModel):
    ids: List[str]


class CreateProductUpdateRequest(JsonModel):
    products: List[ProductUpdateRequestObject]
    replace: str


class QueryProductValuesResponse(JsonModel):
    List[str]


class ProductUpdateResponse(JsonModel):
    products: List[ProductResponseObject]
