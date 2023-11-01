"""This file contains the test functions for products APIs of TestMonitor."""
# Python Modules
from datetime import datetime

# Third party modules
import pytest

# Relative Modules
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClient
from nisystemlink.clients.testmonitor.models import (
    CreateProductsRequest,
    UpdateProductsRequest,
    ProductDeleteRequest,
    ProductField,
    ProductQueryOrderByField,
    ProductRequestObject,
    ProductsAdvancedQuery,
    ProductUpdateRequestObject,
    ProductValuesQuery,
)

product_number = 0

# Constants used in request and response.
FAMILY = "TestProductsApi"
TEST_KEYWORD = ["TestKeyword"]
PROPERTY = {"TestKey": "TestValue"}
FILE_ID = ["TestFileID"]
FILTER = "family == @0"
SUBSTITUTIONS = [FAMILY]
NAME = "name"
INVALID_ID = "invalid_id"
PART_NUMBER_PREFIX = "Test"
PRODUCT_NAME_PREFIX = "Product"
MAX_TIME_DIFF_IN_SECONDS = 15
STARTS_WITH = FAMILY[0]


@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient object."""
    return TestMonitorClient(enterprise_config)


@pytest.fixture(scope="class")
def product_request_object():
    """Fixture to create a request body object of create products API."""

    def _product_request_object():
        global product_number
        product_number += 1

        product_request_object = ProductRequestObject(
            part_number=f"{PART_NUMBER_PREFIX}_{product_number}",
            name=f"{PRODUCT_NAME_PREFIX}_{product_number}",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            file_ids=FILE_ID,
        )
        return product_request_object

    yield _product_request_object


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
def testing_products(create_product, product_request_object):
    """Fixture to create a set of test products."""
    sample_test_products = []
    request_objects = []

    for _ in range(2):
        request_object = product_request_object()
        request_objects.append(request_object)

    request_body = CreateProductsRequest(products=request_objects)
    response = create_product(request_body)

    sample_test_products.extend(response.products)

    return sample_test_products


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClientProducts:
    """Class contains a set of test methods to test Products API of TestMonitor."""

    def test__create_products(self, create_product, product_request_object):
        """Test the case of a completely successful create products API."""
        request_object = [product_request_object()]
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

    def test__create_products__partial_success(self, create_product, product_request_object):
        """Test the case of a partially successful create products API."""
        global product_number

        valid_product = product_request_object()
        duplicate_product = ProductRequestObject(
            part_number=f"{PART_NUMBER_PREFIX}_{product_number}"
        )
        request_body = CreateProductsRequest(products=[valid_product, duplicate_product])
        response = create_product(request_body)

        assert response.error is not None
        assert response.failed is not None
        assert len(response.products) == 1

    def test__get_product(self, client: TestMonitorClient, testing_products):
        """Test the case of completely successful get product API."""
        test_product = testing_products[0]
        product_details = client.get_product(test_product.id)

        assert product_details.part_number == test_product.part_number
        assert product_details.name == test_product.name
        assert product_details.family == FAMILY
        assert product_details.keywords == TEST_KEYWORD
        assert product_details.properties == PROPERTY
        assert product_details.file_ids == FILE_ID

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

        assert first_page_response.continuation_token is not None
        assert first_page_response.total_count is not None

        query.continuation_token = first_page_response.continuation_token

        second_page_response = client.query_products(query_filter=query)

        assert len(second_page_response.products) == 0
        assert second_page_response.total_count is not None
        assert second_page_response.continuation_token is None

    def test__get_products_with_total_count(self, client: TestMonitorClient):
        """Test the case of presence of total count of get products API."""
        response = client.get_products(take=None, continuationToken=None, returnCount=True)
        assert response.total_count is not None

    def test__get_products__without_total_count(self, client: TestMonitorClient):
        """Test the case of no return count of get products API."""
        response = client.get_products(take=None, continuationToken=None, returnCount=False)
        assert response.total_count is None

    def test__delete_product(
        self,
        client: TestMonitorClient,
        create_product,
        product_request_object,
    ):
        """Test the delete product API."""
        product_details = product_request_object()

        request_body = CreateProductsRequest(products=[product_details])
        created_product = create_product(request_body)
        id = created_product.products[0].id

        delete_product_response = client.delete_product(id)

        assert delete_product_response is None

        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(id)

    def test__detele_products(
        self,
        client: TestMonitorClient,
        create_product,
        product_request_object,
    ):
        """Test the delete products API."""
        product_ids = []
        product_request_objects = []

        for _ in range(2):
            product_details = product_request_object()
            product_request_objects.append(product_details)

        request_body = CreateProductsRequest(products=[product_details])
        response = create_product(request_body)
        product_ids.extend([product.id for product in response.products])

        request_body = ProductDeleteRequest(ids=product_ids)
        response = client.delete_products(request_body)

        assert response is None

        for product_id in product_ids:
            with pytest.raises(ApiException, match="404 Not Found"):
                client.get_product(product_id)

    def test__update_products(self, client: TestMonitorClient, testing_products):
        """Test the case of update products API with replace as True."""
        updated_product = ProductUpdateRequestObject(
            id=testing_products[1].id,
            name="Updated_Product_2",
            family=FAMILY,
            keywords=["UpdatedKeyword"],
            properties={"UpdatedKey": "UpdatedValue"},
            file_ids=["UpdatedTestID"],
        )

        request_body = UpdateProductsRequest(products=[updated_product], replace=True)
        response = client.update_products(request_body)

        assert response.products[0].name == updated_product.name
        assert response.products[0].keywords == updated_product.keywords
        assert response.products[0].properties == updated_product.properties
        assert response.products[0].file_ids == updated_product.file_ids

    def test__update_products__without_replacing(
        self,
        client: TestMonitorClient,
        testing_products,
    ):
        """Test the case of update products API without replacing."""
        existing_product = client.get_product(testing_products[0].id)

        updated_product = ProductUpdateRequestObject(
            id=testing_products[0].id,
            name="Updated_Product_1",
            family=FAMILY,
            keywords=["new_keyword"],
            properties={"new_key": "new_value"},
            file_ids=["new_file_id"],
        )

        request_body = UpdateProductsRequest(products=[updated_product], replace=False)
        response = client.update_products(request_body)

        assert response.products[0].name == updated_product.name
        assert len(response.products[0].keywords) == len(existing_product.keywords) + 1
        assert len(response.products[0].properties) == len(existing_product.properties) + 1
        assert len(response.products[0].file_ids) == len(existing_product.file_ids) + 1

    def test__update_products__partial_success(self, client: TestMonitorClient, testing_products):
        """Test the case of a partially successful update products API."""
        valid_updated_product = ProductUpdateRequestObject(
            id=testing_products[0].id,
            name="Updated_Product_1",
            family=FAMILY,
            keywords=["new_keyword_2"],
            properties={"new_key_2": "new_value_2"},
            file_ids=["new_fileID_2"],
        )

        invalid_product = ProductUpdateRequestObject(id=INVALID_ID)

        # Update multiple products with one of the products being invalid and check the response.
        request_body = UpdateProductsRequest(
            products=[valid_updated_product, invalid_product],
            replace=False,
        )

        response = client.update_products(request_body)

        assert len(response.products) == 1
        assert response.failed is not None
        assert response.error is not None

    def test__query_product_values(self, client: TestMonitorClient):
        """Test the query product values API."""
        request_body = ProductValuesQuery(
            field="FAMILY",
            filter=FILTER,
            substitutions=SUBSTITUTIONS,
            startsWith=STARTS_WITH,
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 1
