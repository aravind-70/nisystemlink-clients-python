"""This file contains the test functions for products APIs of TestMonitor."""
# Python Modules
from datetime import datetime

# Third party modules
import pytest

# Relative Modules
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClient, models

# Constants used in request and response.
FAMILY = "TestProductsApi"
TEST_KEYWORD = ["TestKeyword"]
PROPERTY = {"TestKey": "TestValue"}
FILE_ID = ["TestFileID"]
FILTER = "family == @0"
SUBSTITUTIONS = ["TestProductsApi"]
NAME = "name"
INVALID_ID = "invalid id"
PART_NUMBER = "PART_NUMBER"

@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient instance."""
    return TestMonitorClient(enterprise_config)


@pytest.fixture(scope="class")
def create_product(client):
    """Fixture to return a factory that creates products."""
    products = []
    product_ids = []

    def _create_product(product):
        response = client.create_products(product)
        products.append(response)
        product_ids.extend([product.id for product in response.products])
        return response

    yield _create_product

    request_body = models.ProductDeleteRequest(ids=product_ids)
    client.delete_products(request_body)


@pytest.fixture(scope="class")
def product_request_body():
    """Fixture to create a request body object of create_products API."""

    def _product_request_body(product_no):
        product_request_object = models.ProductRequestObject(
            partNumber=f"Test_{product_no}",
            name=f"TestProduct_{product_no}",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            fileIds=FILE_ID,
        )

        return product_request_object

    yield _product_request_body


@pytest.fixture(scope="class")
def create_test_products(create_product, product_request_body):
    """Fixture to create a set of test products."""
    sample_test_products = []
    request_objects = []

    for product_no in range(1, 3):
        request_object = product_request_body(product_no)
        request_objects.append(request_object)

    request_body = models.CreateProductsRequest(products=request_objects)
    response = create_product(request_body)
    sample_test_products.append(response)

    return sample_test_products


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClienProductst:
    """Class contains a set of test methods to test Products API."""

    def test__create_products(self, create_product, product_request_body):
        request_object = [product_request_body(3)]
        request_body = models.CreateProductsRequest(products=request_object)
        response = create_product(request_body)

        assert len(response.products) == 1

        assert response.products[0].part_number == request_body.products[0].part_number
        assert response.products[0].name == request_body.products[0].name
        assert response.products[0].family == request_body.products[0].family
        assert response.products[0].keywords == request_body.products[0].keywords
        assert response.products[0].properties == request_body.products[0].properties
        assert response.products[0].file_ids == request_body.products[0].file_ids

        assert response.failed is None
        assert response.error is None

    def test__create_products__partial_success(self, create_product, product_request_body):
        request_objects = [product_request_body(3), product_request_body(4)]
        request_body = models.CreateProductsRequest(products=request_objects)
        response = create_product(request_body)

        assert len(response.products) == 1
        assert response.error is not None
        assert response.failed is not None

    def test__get_product(self, client, create_test_products):
        product_details = client.get_product(create_test_products[0].products[0].id)

        assert product_details.part_number == create_test_products[0].products[0].part_number
        assert product_details.name == create_test_products[0].products[0].name
        assert product_details.family == FAMILY
        assert product_details.keywords == TEST_KEYWORD
        assert product_details.properties == PROPERTY
        assert product_details.file_ids == FILE_ID

        updated_at_timestamp = product_details.updated_at.timestamp()
        current_timestamp = datetime.now().timestamp()
        assert updated_at_timestamp == pytest.approx(current_timestamp, abs=15)

    def test__get_product__invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(INVALID_ID)

    def test__query_product(self, client):
        first_page_response = client.query_products(
            models.ProductsAdvancedQuery(
                filter=FILTER,
                substitutions=SUBSTITUTIONS,
                order_by=models.ProductQueryOrderByField(PART_NUMBER),
                descending=False,
                projection=[models.ProductField(PART_NUMBER)],
                take=1,
                return_count=True,
            )
        )

        assert len(first_page_response.products) == 1
        assert first_page_response.continuation_token is not None
        assert first_page_response.total_count is not None

        continuation_token = first_page_response.continuation_token

        second_page_response = client.query_products(
            models.ProductsAdvancedQuery(
                filter=FILTER,
                substitutions=SUBSTITUTIONS,
                order_by=models.ProductQueryOrderByField(PART_NUMBER),
                descending=False,
                projection=[models.ProductField(PART_NUMBER)],
                continuation_token=continuation_token,
                return_count=True,
            )
        )

        assert len(second_page_response.products) == 3
        assert second_page_response.total_count is not None

    def test__get_products(self, client):
        response = client.get_products(
            take=1, continuationToken=None, returnCount=True
        )

        assert response.total_count is not None

    def test__get_products__without_return_count(self, client):
        response = client.get_products(
            take=None, continuationToken=None, returnCount=False
        )
        assert response.total_count is None

    def test__delete_product(self, client):
        product_details = models.ProductRequestObject(
            partNumber="Test_5",
            name="TestProduct_5",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            fileIds=FILE_ID,
        )
        request_body = models.CreateProductsRequest(products=[product_details])
        response = client.create_products(request_body)
        id = response.products[0].id

        response = client.delete_product(id)
        assert response is None

        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product(id)

    def test__detele_products(self, client):
        ids = []
        for part_no in range(6, 8):
            product_details = models.ProductRequestObject(
                partNumber=f"Test_{part_no}",
                name=f"TestProduct_{part_no}",
                family=FAMILY,
                keywords=TEST_KEYWORD,
                properties=PROPERTY,
                fileIds=FILE_ID,
            )

            request_body = models.CreateProductsRequest(products=[product_details])
            response = client.create_products(request_body)
            ids.append(response.products[0].id)

        request_body = models.ProductDeleteRequest(ids=ids)
        response = client.delete_products(request_body)
        assert response is None

        for id in ids:
            with pytest.raises(ApiException, match="404 Not Found"):
                client.get_product(id)

    def test__update_products(self, client, create_test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[0].products[0].id,
            name="Updated_TestProduct_2",
            family=FAMILY,
            keywords=["UpdatedKeyword"],
            properties={"UpdatedKey": "UpdatedValue"},
            file_ids=["UpdatedTestID"],
        )

        request_body = models.CreateProductUpdateRequest(products=[updated_product], replace=True)
        response = client.update_products(request_body)

        assert response.products[0].name == updated_product.name
        assert response.products[0].keywords == updated_product.keywords
        assert response.products[0].properties == updated_product.properties
        assert response.products[0].file_ids == updated_product.file_ids

    def test__update_products__without_replacing(self, client, create_test_products):
        existing_product = client.get_product(create_test_products[0].products[0].id)

        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[0].products[0].id,
            name="Updated_TestProduct_1",
            family=FAMILY,
            keywords=["new_keyword"],
            properties={"new_key": "new_value"},
            fileIds=["new_file_id"],
        )

        request_body = models.CreateProductUpdateRequest(products=[updated_product], replace=False)
        response = client.update_products(request_body)

        assert response.products[0].name == updated_product.name
        assert len(response.products[0].keywords) == len(existing_product.keywords) + 1
        assert len(response.products[0].properties) == len(existing_product.properties) + 1
        assert len(response.products[0].file_ids) == len(existing_product.file_ids) + 1

    def test__update_products__partial_success(self, client, create_test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[0].products[0].id,
            name="Updated_TestProduct_1",
            family=FAMILY,
            keywords=["new_keyword_2"],
            properties={"new_key_2": "new_value_2"},
            fileIds=["new_fileID_2"],
        )

        invalid_product = models.ProductUpdateRequestObject(id=INVALID_ID)

        request_body = models.CreateProductUpdateRequest(
            products=[updated_product, invalid_product], replace=False
        )

        response = client.update_products(request_body)

        assert response.failed is not None
        assert response.error is not None

    def test__query_product_values(self, client):
        request_body = models.ProductValuesQuery(
            field=PART_NUMBER,
            filter=FILTER,
            substitutions=SUBSTITUTIONS,
            startsWith="T",
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 4
