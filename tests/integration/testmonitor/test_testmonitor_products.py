"""This file contains the test class for products APIs of TestMonitor."""
# Python Modules
from datetime import datetime
from typing import Callable, List

# Third party modules
import pytest
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClient
from nisystemlink.clients.testmonitor.models import (
    CreateProductsRequest,
    ProductDeleteRequest,
    ProductField,
    ProductQueryOrderByField,
    ProductRequestObject,
    ProductResponseObject,
    ProductsAdvancedQuery,
    ProductUpdateRequestObject,
    ProductValuesQuery,
    ProductValuesQueryField,
    UpdateProductsRequest,
)

# Constants used in request and response.
PART_NUMBER_PREFIX = "Test"
PRODUCT_NAME_PREFIX = "Product"
FAMILY = "TestProductsApi"
TEST_KEYWORD = ["TestKeyword"]
PROPERTY = {"TestKey": "TestValue"}
FILE_ID = ["TestFileID"]
FILTER = "family == @0"
SUBSTITUTIONS = [FAMILY]
STARTS_WITH = FAMILY[0]

NAME = "name"
MAX_TIME_DIFF_IN_SECONDS = 15
INVALID_ID = "invalid_id"

UPDATED_NAME = "UpdatedProduct"
UPDATED_KEYWORD = ["UpdatedKeyword"]
UPDATED_PROPERTIES = {"UpdatedKey": "UpdatedValue"}
UPDATED_FILE_ID = ["UpdatedTestFileId"]


@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient object."""
    return TestMonitorClient(enterprise_config)


@pytest.fixture(scope="class")
def get_product_number():
    """Fixture to update the product number."""
    product_number = 0

    def _get_product_number():
        nonlocal product_number
        product_number += 1
        return product_number

    yield _get_product_number


@pytest.fixture(scope="class")
def create_product_request(get_product_number: Callable):
    """Fixture to create a request body object of create products API."""

    def _create_product_request():
        product_number = get_product_number()

        product_request = ProductRequestObject(
            part_number=f"{PART_NUMBER_PREFIX}_{product_number}",
            name=f"{PRODUCT_NAME_PREFIX}_{product_number}",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            file_ids=FILE_ID,
        )
        return product_request

    yield _create_product_request


@pytest.fixture(scope="class")
def update_product_request():
    """Fixture to create a request body object of update products API."""

    def _update_product_request(
        id,
        name=UPDATED_NAME,
        family=FAMILY,
        keywords=UPDATED_KEYWORD,
        properties=UPDATED_PROPERTIES,
        file_ids=UPDATED_FILE_ID,
    ):
        product_details = ProductUpdateRequestObject(
            id=id,
            name=name,
            family=family,
            keywords=keywords,
            properties=properties,
            file_ids=file_ids,
        )

        return product_details

    yield _update_product_request


@pytest.fixture(scope="class")
def create_product(client: TestMonitorClient):
    """Fixture to return a object that creates products."""
    product_ids = []

    def _create_product(product):
        response = client.create_products(product)
        # Append the product ids to delete the product after tests are executed.
        product_ids.extend([product.id for product in response.products])
        return response

    yield _create_product

    # Delete the created products after the tests are completed.
    request_body = ProductDeleteRequest(ids=product_ids)
    client.delete_products(request_body)


@pytest.fixture(scope="class")
def test_products(create_product: Callable, create_product_request: Callable):
    """Fixture to create a set of test products."""
    sample_test_products = []

    request_objects = [create_product_request() for _ in range(4)]
    request_body = CreateProductsRequest(products=request_objects)

    response = create_product(request_body)
    sample_test_products.extend(response.products)

    return sample_test_products


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClientProducts:
    """Class contains a set of test methods to test Products API of TestMonitor."""

    def test__create_products__complete_success(
        self,
        create_product: Callable,
        create_product_request: Callable,
    ):
        """Test the case of a completely successful create products API."""
        request_object = [create_product_request()]
        request_body = CreateProductsRequest(products=request_object)
        response = create_product(request_body)

        assert response.failed is None
        assert response.error is None

        assert len(response.products) == 1

        requested_product = request_body.products[0]
        created_product = response.products[0]

        assert created_product.part_number == requested_product.part_number
        assert created_product.name == requested_product.name
        assert created_product.family == requested_product.family
        assert created_product.keywords == requested_product.keywords
        assert created_product.properties == requested_product.properties
        assert created_product.file_ids == requested_product.file_ids

    def test__create_products__partial_success(
        self,
        create_product: Callable,
        create_product_request: Callable,
        get_product_number: Callable,
    ):
        """Test the case of a partially successful create products API."""
        valid_product = create_product_request()

        # Get the previous product number to create a invalid product.
        product_number = get_product_number() - 1

        duplicate_product = ProductRequestObject(
            part_number=f"{PART_NUMBER_PREFIX}_{product_number}"
        )
        request_body = CreateProductsRequest(products=[valid_product, duplicate_product])
        response = create_product(request_body)

        assert response.error is not None
        assert response.failed is not None
        assert len(response.products) == 1

    def test__get_product(
        self,
        client: TestMonitorClient,
        test_products: List[ProductResponseObject],
    ):
        """Test the case of completely successful get product API."""
        test_product = test_products[0]
        product_details = client.get_product(test_product.id)

        assert product_details.part_number == test_product.part_number
        assert product_details.name == test_product.name
        assert product_details.family == test_product.family
        assert product_details.keywords == test_product.keywords
        assert product_details.properties == test_product.properties
        assert product_details.file_ids == test_product.file_ids

        updated_at_timestamp = product_details.updated_at.timestamp()
        current_timestamp = datetime.now().timestamp()
        assert updated_at_timestamp == pytest.approx(
            current_timestamp,
            abs=MAX_TIME_DIFF_IN_SECONDS,
        )

    def test__get_product__invalid_id(self, client: TestMonitorClient):
        """Test the case of get product API with invalid id."""
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(INVALID_ID)

    def test__query_product(self, client: TestMonitorClient):
        """Test the cases of query products API."""
        query = ProductsAdvancedQuery(
            filter=FILTER,
            substitutions=SUBSTITUTIONS,
            order_by=ProductQueryOrderByField.PART_NUMBER,
            descending=False,
            projection=[ProductField.PART_NUMBER],
            return_count=True,
        )

        first_page_response = client.query_products(query_filter=query)

        assert len(first_page_response.products) > 0
        assert first_page_response.total_count > 0
        assert first_page_response.continuation_token is not None

        query.continuation_token = first_page_response.continuation_token

        second_page_response = client.query_products(query_filter=query)

        assert len(second_page_response.products) == 0
        assert second_page_response.total_count > 0
        assert second_page_response.continuation_token is None

    def test__get_products__continutation_token(self, client: TestMonitorClient):
        """Test the case of continuation token to become null for get products API."""
        continuation_token = None

        while True:
            response = client.get_products(
                continuationToken=continuation_token,
                take=None,
                returnCount=True,
            )
            continuation_token = response.continuation_token

            if continuation_token is None:
                break

    def test__get_products__with_total_count(self, client: TestMonitorClient):
        """Test the case of presence of total count of get products API."""
        response = client.get_products(take=None, continuationToken=None, returnCount=True)
        assert response.total_count > 0

    def test__get_products__without_total_count(self, client: TestMonitorClient):
        """Test the case of no return count of get products API."""
        response = client.get_products(take=None, continuationToken=None, returnCount=False)
        assert response.total_count is None

    def test__delete_product__success(
        self,
        client: TestMonitorClient,
        create_product: Callable,
        create_product_request: Callable,
    ):
        """Test the delete product API."""
        product_details = create_product_request()

        request_body = CreateProductsRequest(products=[product_details])
        created_product = create_product(request_body)
        id = created_product.products[0].id

        delete_product_response = client.delete_product(id)

        assert delete_product_response is None

        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(id)

    def test__delete_products__success(
        self,
        client: TestMonitorClient,
        create_product: Callable,
        create_product_request: Callable,
    ):
        """Test the delete products API."""
        product_ids = []

        product_request_objects = [create_product_request() for _ in range(2)]
        request_body = CreateProductsRequest(products=product_request_objects)

        response = create_product(request_body)
        product_ids.extend([product.id for product in response.products])

        request_body = ProductDeleteRequest(ids=product_ids)
        response = client.delete_products(request_body)

        assert response is None

        for product_id in product_ids:
            with pytest.raises(ApiException, match="404 Not Found"):
                client.get_product(product_id)

    def test__update_products(
        self,
        client: TestMonitorClient,
        test_products: List[ProductResponseObject],
        update_product_request: Callable,
    ):
        """Test the case of update products API with replace as True."""
        new_product_details = update_product_request(id=test_products[1].id)

        request_body = UpdateProductsRequest(products=[new_product_details], replace=True)
        response = client.update_products(request_body)
        updated_product = response.products[0]

        assert updated_product.name == new_product_details.name
        assert updated_product.keywords == new_product_details.keywords
        assert updated_product.properties == new_product_details.properties
        assert updated_product.file_ids == new_product_details.file_ids

    def test__update_products__without_replacing(
        self,
        client: TestMonitorClient,
        test_products: List[ProductResponseObject],
        update_product_request: Callable,
    ):
        """Test the case of update products API without replacing."""
        existing_product = client.get_product(test_products[2].id)

        new_product_details = update_product_request(
            id=test_products[2].id,
            keywords=["second_keyword"],
            properties={"second_key": "second_value"},
            file_ids=["second_file_id"],
        )

        request_body = UpdateProductsRequest(products=[new_product_details], replace=False)
        response = client.update_products(request_body)
        updated_product = response.products[0]

        assert updated_product.name == new_product_details.name
        assert len(updated_product.keywords) == len(existing_product.keywords) + 1
        assert len(updated_product.properties) == len(existing_product.properties) + 1
        assert len(updated_product.file_ids) == len(existing_product.file_ids) + 1

    def test__update_products__partial_success(
        self,
        client: TestMonitorClient,
        test_products: List[ProductResponseObject],
        update_product_request: Callable,
    ):
        """Test the case of a partially successful update products API."""
        valid_product_updation = update_product_request(id=test_products[3].id)
        invalid_product_updation = update_product_request(id=INVALID_ID)

        # Update multiple products with one of the products being invalid and check the response.
        request_body = UpdateProductsRequest(
            products=[valid_product_updation, invalid_product_updation],
            replace=False,
        )

        response = client.update_products(request_body)

        assert len(response.products) == 1
        assert response.failed is not None
        assert response.error is not None

    def test__query_product_values(self, client: TestMonitorClient):
        """Test the query product values API."""
        request_body = ProductValuesQuery(
            field=ProductValuesQueryField.FAMILY,
            filter=FILTER,
            substitutions=SUBSTITUTIONS,
            startsWith=STARTS_WITH,
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 1
