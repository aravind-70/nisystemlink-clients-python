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
    CreateProductUpdateRequest,
    ProductDeleteRequest,
    ProductField,
    ProductQueryOrderByField,
    ProductRequestObject,
    ProductsAdvancedQuery,
    ProductUpdateRequestObject,
    ProductValuesQuery,
)

# Constants used in request and response.
FAMILY = "TestProductsApi"
TEST_KEYWORD = ["TestKeyword"]
PROPERTY = {"TestKey": "TestValue"}
FILE_ID = ["TestFileID"]
FILTER = "family == @0"
SUBSTITUTIONS = ["TestProductsApi"]
NAME = "name"
INVALID_ID = "invalid_id"
PART_NUMBER = "PART_NUMBER"
PART_NUMBER_PREFIX = "Test"
PRODUCT_NAME_PREFIX = "Product"
FIRST_PRODUCT = 0
SECOND_PRODUCT = 1
MAX_TIME_DIFF = 15
STARTS_WITH = "T"


@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient object."""
    return TestMonitorClient(enterprise_config)


@pytest.fixture(scope="class")
def create_product(client):
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
def product_request_object():
    """Fixture to create a request body object of create products API."""

    def _product_request_object(product_num):
        product_request_object = ProductRequestObject(
            part_number=f"{PART_NUMBER_PREFIX}_{product_num}",
            name=f"{PRODUCT_NAME_PREFIX}_{product_num}",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            file_ids=FILE_ID,
        )

        return product_request_object

    yield _product_request_object


@pytest.fixture(scope="class")
def create_test_products(create_product, product_request_object):
    """Fixture to create a set of test products."""
    sample_test_products = []
    request_objects = []

    for product_num in range(1, 3):
        request_object = product_request_object(product_num)
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
        # Create a product and check the response.
        request_object = [product_request_object(3)]
        request_body = CreateProductsRequest(products=request_object)
        response = create_product(request_body)

        assert len(response.products) == 1

        assert (
            response.products[FIRST_PRODUCT].part_number
            == request_body.products[FIRST_PRODUCT].part_number
        )
        assert response.products[FIRST_PRODUCT].name == request_body.products[FIRST_PRODUCT].name
        assert (
            response.products[FIRST_PRODUCT].family == request_body.products[FIRST_PRODUCT].family
        )
        assert (
            response.products[FIRST_PRODUCT].keywords
            == request_body.products[FIRST_PRODUCT].keywords
        )
        assert (
            response.products[FIRST_PRODUCT].properties
            == request_body.products[FIRST_PRODUCT].properties
        )
        assert (
            response.products[FIRST_PRODUCT].file_ids
            == request_body.products[FIRST_PRODUCT].file_ids
        )

        assert response.failed is None
        assert response.error is None

    def test__create_products__partial_success(self, create_product, product_request_object):
        """Test the case of a partially successful create products API."""
        # Create multiple products with one of products as invalid and check the response.
        request_objects = [product_request_object(3), product_request_object(4)]
        request_body = CreateProductsRequest(products=request_objects)
        response = create_product(request_body)

        assert len(response.products) == 1
        assert response.error is not None
        assert response.failed is not None

    def test__get_product(self, client, create_test_products):
        """Test the case of completely successful get product API."""
        product_details = client.get_product(
            create_test_products[FIRST_PRODUCT].id
        )

        assert (
            product_details.part_number
            == create_test_products[FIRST_PRODUCT].part_number
        )
        assert (
            product_details.name == create_test_products[FIRST_PRODUCT].name
        )
        assert product_details.family == FAMILY
        assert product_details.keywords == TEST_KEYWORD
        assert product_details.properties == PROPERTY
        assert product_details.file_ids == FILE_ID

        updated_at_timestamp = product_details.updated_at.timestamp()
        current_timestamp = datetime.now().timestamp()
        assert updated_at_timestamp == pytest.approx(current_timestamp, abs=MAX_TIME_DIFF)

    def test__get_product__invalid_id(self, client):
        """Test the case of get product API with invalid id."""
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(INVALID_ID)

    def test__query_product(self, client):
        """Test the cases of query products API."""
        first_page_response = client.query_products(
            ProductsAdvancedQuery(
                filter=FILTER,
                substitutions=SUBSTITUTIONS,
                order_by=ProductQueryOrderByField(PART_NUMBER),
                descending=False,
                projection=[ProductField(PART_NUMBER)],
                take=4,
                return_count=True,
            )
        )

        assert len(first_page_response.products) == 4
        assert first_page_response.continuation_token is not None
        assert first_page_response.total_count is not None

        continuation_token = first_page_response.continuation_token

        second_page_response = client.query_products(
            ProductsAdvancedQuery(
                filter=FILTER,
                substitutions=SUBSTITUTIONS,
                order_by=ProductQueryOrderByField(PART_NUMBER),
                descending=False,
                projection=[ProductField(PART_NUMBER)],
                continuation_token=continuation_token,
                return_count=True,
            )
        )

        assert len(second_page_response.products) == 0
        assert second_page_response.total_count is not None
        assert second_page_response.continuation_token is None

    def test__get_products(self, client):
        """Test the case of presence of return count of get products API."""
        response = client.get_products(
            take=None,
            continuationToken=None,
            returnCount=True,
        )
        assert response.total_count is not None

        continuation_token = response.continuation_token

        # Loop until all the products are returned.
        while continuation_token is not None:
            response = client.get_products(
                take=None,
                continuationToken=continuation_token,
                returnCount=True,
            )
            continuation_token = response.continuation_token

        assert response.continuation_token is None

    def test__get_products__without_return_count(self, client):
        """Test the case of no return count of get products API."""
        response = client.get_products(take=None, continuationToken=None, returnCount=False)
        assert response.total_count is None

    def test__delete_product(self, client):
        """Test the delete product API."""
        product_details = ProductRequestObject(
            part_number="Test_5",
            name="Product_5",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            file_ids=FILE_ID,
        )

        request_body = CreateProductsRequest(products=[product_details])
        create_product_response = client.create_products(request_body)
        id = create_product_response.products[FIRST_PRODUCT].id

        delete_product_response = client.delete_product(id)

        assert delete_product_response is None

        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(id)

    def test__detele_products(self, client):
        """Test the delete products API."""
        ids = []
        for product_num in range(6, 8):
            product_details = ProductRequestObject(
                part_number=f"{PART_NUMBER_PREFIX}_{product_num}",
                name=f"{PRODUCT_NAME_PREFIX}_{product_num}",
                family=FAMILY,
                keywords=TEST_KEYWORD,
                properties=PROPERTY,
                file_ids=FILE_ID,
            )

            request_body = CreateProductsRequest(products=[product_details])
            response = client.create_products(request_body)
            ids.append(response.products[FIRST_PRODUCT].id)

        request_body = ProductDeleteRequest(ids=ids)
        response = client.delete_products(request_body)

        assert response is None

        for id in ids:
            with pytest.raises(ApiException, match="404 Not Found"):
                client.get_product(id)

    def test__update_products(self, client, create_test_products):
        """Test the case of update products API with replace as True."""
        updated_product = ProductUpdateRequestObject(
            id=create_test_products[1].id,
            name="Updated_Product_2",
            family=FAMILY,
            keywords=["UpdatedKeyword"],
            properties={"UpdatedKey": "UpdatedValue"},
            file_ids=["UpdatedTestID"],
        )

        request_body = CreateProductUpdateRequest(products=[updated_product], replace=True)
        response = client.update_products(request_body)

        assert response.products[FIRST_PRODUCT].name == updated_product.name
        assert response.products[FIRST_PRODUCT].keywords == updated_product.keywords
        assert response.products[FIRST_PRODUCT].properties == updated_product.properties
        assert response.products[FIRST_PRODUCT].file_ids == updated_product.file_ids

    def test__update_products__without_replacing(self, client, create_test_products):
        """Test the case of update products API without replacing."""
        existing_product = client.get_product(
            create_test_products[FIRST_PRODUCT].id
        )

        updated_product = ProductUpdateRequestObject(
            id=create_test_products[FIRST_PRODUCT].id,
            name="Updated_Product_1",
            family=FAMILY,
            keywords=["new_keyword"],
            properties={"new_key": "new_value"},
            file_ids=["new_file_id"],
        )

        request_body = CreateProductUpdateRequest(products=[updated_product], replace=False)
        response = client.update_products(request_body)

        assert response.products[FIRST_PRODUCT].name == updated_product.name
        assert len(response.products[FIRST_PRODUCT].keywords) == len(existing_product.keywords) + 1
        assert (
            len(response.products[FIRST_PRODUCT].properties) == len(existing_product.properties) + 1
        )
        assert len(response.products[FIRST_PRODUCT].file_ids) == len(existing_product.file_ids) + 1

    def test__update_products__partial_success(self, client, create_test_products):
        """Test the case of a partially successful update products API."""

        # Update multiple products with one of products as invalid and check the response.
        valid_updated_product = ProductUpdateRequestObject(
            id=create_test_products[FIRST_PRODUCT].id,
            name="Updated_Product_1",
            family=FAMILY,
            keywords=["new_keyword_2"],
            properties={"new_key_2": "new_value_2"},
            file_ids=["new_fileID_2"],
        )

        invalid_product = ProductUpdateRequestObject(id=INVALID_ID)
        request_body = CreateProductUpdateRequest(
            products=[valid_updated_product, invalid_product],
            replace=False,
        )

        response = client.update_products(request_body)

        assert len(response.products) == 1
        assert response.failed is not None
        assert response.error is not None

    def test__query_product_values(self, client):
        """Test the query product values API."""
        request_body = ProductValuesQuery(
            field=PART_NUMBER,
            filter=FILTER,
            substitutions=SUBSTITUTIONS,
            startsWith=STARTS_WITH,
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 4
