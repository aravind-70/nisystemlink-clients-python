"""Implementation of TestMonitorClient."""
# Python Module
from typing import Optional

# Relative modules
from nisystemlink.clients import core
from nisystemlink.clients.core._uplink._base_client import BaseClient
from nisystemlink.clients.core._uplink._methods import delete, get, post
from uplink import Query

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
            ApiException: if unable to communicate with the TestMonitor Service.
        """
        if configuration is None:
            configuration = core.JupyterHttpConfiguration()

        super().__init__(configuration, "/nitestmonitor/v2/")

    # products
    @post("products")
    def create_products(
        self,
        products: models.CreateProductsRequest,
    ) -> models.ProductsSuccessResponse:
        """Create a new products with the provided product details.

        Args:
            products: The request to create the products.

        Returns:
            The product details of the newly created products.

        """
        ...

    @get("products/{productId}")
    def get_product(self, productId: str) -> models.ProductResponseObject:
        """Retrieves the product details single product identified by its ID.

        Args:
            productId: Unique ID of a product.

        Returns:
            The details of the product.
        """
        ...

    @get("products", args=[Query, Query, Query])
    def get_products(
        self,
        continuationToken: str,
        take: int,
        returnCount: bool,
    ) -> models.ProductsQueryResponse:
        """Get product details of multiple products.

        Args:
            continuationToken: The token used to paginate results.
            take: Limits the returned list of products to the specified number
            returnCount: Total count of the products available.

        Returns:
            The list of products.
        """
        ...

    @post("query-products")
    def query_products(
        self,
        query_filter: models.ProductsAdvancedQuery,
    ) -> models.ProductsQueryResponse:
        """Get a set of products based on the queryFilter.

        Args:
            query_filter: The filter to be applied when querying for products.

        Returns:
            The list of products.
        """
        ...

    @delete("products/{productId}")
    def delete_product(self, productId: str) -> None:
        """Delete a product using the product id.

        Args:
            product_id: The id of the product to be deleted.

        Returns:
            None
        """
        ...

    @post("delete-products")
    def delete_products(self, request_body: models.ProductDeleteRequest) -> None:
        """Delete set of products using the list of product ids given in the request body.

        Args:
            request_body: The list of ids to be deleted.

        Returns:
            None
        """
        ...

    @post("update-products")
    def update_products(
        self,
        request_body: models.UpdateProductsRequest,
    ) -> models.ProductsSuccessResponse:
        """Update a set of products.

        Args:
            request_body: The product details to be updated with.

        Returns:
            The updated product response.
        """
        ...

    @post("query-product-values")
    def query_product_values(self, product_query: models.ProductValuesQuery):
        """Get product values or fields using the product_query.

        Args:
            product_query: The fields to be queried based on filter.

        Returns:
            The list of values based on the product_query.
        """
        ...
