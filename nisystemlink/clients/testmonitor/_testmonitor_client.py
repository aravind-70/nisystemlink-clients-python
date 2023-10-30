"""Implementation of TestMonitorClient."""

from typing import Optional


from nisystemlink.clients import core
from nisystemlink.clients.core._uplink._base_client import BaseClient
from nisystemlink.clients.core._uplink._methods import delete, get, post
from uplink import Body, Path, Query

from . import models


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
            ApiException: if unable to communicate with the DataFrame Service.
        """
        if configuration is None:
            configuration = core.JupyterHttpConfiguration()

        super().__init__(configuration, "/nitestmonitor/v2/")

    # versioning

    @get("")
    def api_info(self) -> models.ApiInfo:
        """Get the information about the available APIs."""
        ...

    # Products APIs.
    @post("products")
    def create_products(
        self, products: models.CreateProductsRequest
    ) -> models.CreateProductsResponse:
        """Create products using the create product API."""
        ...

    @get("products/{productId}", args=[Path, Body])
    def get_product(self, productId: str) -> models.ProductResponseObject:
        """Get product details using the product id."""
        ...

    @get("products", args=[Path, Body])
    def get_products(
        self,
        continuationToken: Query(type=str),
        take: Query(type=int),
        returnCount: Query(type=bool),
    ) -> models.ProductsQueryResponse:
        """Get a set of products."""
        ...

    @post("query-products", args=[Path, Body])
    def query_products(
        self, queryFilter: Body(type=models.ProductsAdvancedQuery)
    ) -> models.ProductsQueryResponse:
        """Get a set of products based on the queryFilter."""
        ...

    @delete("products/{productId}", args=[Path, Body])
    def delete_product(self, productId: str) -> None:
        """Delete a product using the product id."""
        ...

    @post("delete-products", args=[Path, Body])
    def delete_products(self, requestBody: Body(type=models.ProductDeleteRequest)) -> None:
        """Delete set of products using the list of product ids given in the request body."""
        ...

    @post("update-products", args=[Path, Body])
    def update_products(
        self, request: Body(type=models.CreateProductUpdateRequest)
    ) -> models.ProductUpdateResponse:
        """Update a set of products."""
        ...

    @post("query-product-values", args=[Path, Body])
    def query_product_values(self, productQuery: Body(type=models.ProductValuesQuery)):
        """Get product values or fields using the productQuery."""
        ...

    # # results

    # @post("query-results", args=[Path, Body])
    # def query_results(
    #     self, queryFilter: Body(type=models.ResultsAdvancedQuery)
    # ) -> models.ResultsQueryResponseObject:
    #     ...

    # @get("results", args=[Path, Body])
    # def get_results(
    #     self,
    #     continuationToken: Query(type=str),
    #     take: Query(type=int),
    #     returnCount: Query(type=int),
    # ) -> models.ResultsQueryResponse:
    #     ...

    # @post("results", args=[Path, Body])
    # def create_results(self, requestBody: Body(type=models.CreateTestResultRequest)):
    #     ...

    # @get("results/{resultId}", args=[Path, Body])
    # def get_result(self, resultId: str) -> models.TestResultResponse:
    #     ...

    # @delete("results/{resultId}", args=[Path, Body])
    # def delete_result(self, resultId: str, deleteSteps: Query(type=bool) = True):
    #     ...

    # @post("query-result-values", args=[Path, Body])
    # def query_result_values(self, resultQuery: Body(type=models.ResultValuesQuery)):
    #     ...

    # @post("update-results", args=[Path, Body])
    # def update_results(self, request: Body(type=models.UpdateTestResultsRequest)):
    #     ...

    # @post("delete-results", args=[Path, Body])
    # def delete_results(self, requestBody: Body(type=models.TestStepsDeleteRequest)):
    #     ...

    # # steps

    # # paths

    # @get("paths")
    # def get_paths(
    #     self,
    #     continuationToken: Query(type=str),
    #     take: Query(type=int),
    #     returnCount: Query(type=int),
    # ) -> models.PathsQueryResponse:
    #     ...

    # @get("paths/{pathId}")
    # def get_path(self, pathId: str) -> models.PathResponse:
    #     ...

    # @post("query-paths")
    # def query_paths(
    #     self, queryFilter: Body(type=models.PathsAdvancedQuery)
    # ) -> models.PathsQueryResponse:
    #     ...
