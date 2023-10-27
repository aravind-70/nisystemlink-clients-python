"""This file contains the test functions for products APIs of TestMonitor."""
# Python Modules
from datetime import datetime

# Third party modules
import pytest
from pydantic import ValidationError

# Relative Modules
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClient, models

# Constants used in request and response.
FILTER = "family==\"TestProductsApi\""
FAMILY = "TestProductsApi"
TEST_KEYWORD = ["TestKeyword"]
PROPERTY = {"TestKey": "TestValue"}
FILE_ID = ["TestFileID"]


@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient instance."""
    return TestMonitorClient(enterprise_config)


@pytest.fixture(scope="class")
def create_product(client):
    """Fixture to return a factory that creates products."""
    products = []

    def _create_product(product):
        response = client.create_products(product)
        products.append(response)
        return response

    yield _create_product


@pytest.fixture(scope="class")
def create_test_products(create_product):
    """Fixture to create a set of test products."""
    sample_test_products = []

    for part_no in range(1, 3):
        product_details = models.ProductRequestObject(
            partNumber=f"Test_{part_no}",
            name=f"TestProduct_{part_no}",
            family=FAMILY,
            keywords=TEST_KEYWORD,
            properties=PROPERTY,
            fileIds=FILE_ID,
        )

        request_body = models.CreateProductsRequest(products=[product_details])
        response = create_product(request_body)
        sample_test_products.append(response)

    return sample_test_products


@pytest.fixture(scope="class")
def product_request_body(part_no):
    """Fixture to create a request body object of create_products API."""
    product_request_object = models.ProductRequestObject(
        partNumber=f"Test_{part_no}",
        name=f"TestProduct_{part_no}",
        family=FAMILY,
        keywords=TEST_KEYWORD,
        properties=PROPERTY,
        fileIds=FILE_ID,
    )

    request_body = models.CreateProductsRequest(products=[product_request_object])

    return request_body


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClient:
    """Class contains a set of test methods to test Products API."""

    def test__create_products(self, create_product, product_request_body):
        response = create_product(product_request_body(3))
        assert len(response.products) == 1

    def test__create_products__partial_success(self, create_product, product_request_body):
        with pytest.raises(ValidationError) as exc_info:
            create_product(product_request_body(3))

        assert "error" in str(exc_info)
        assert "failed" in str(exc_info)

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
        assert updated_at_timestamp == pytest.approx(current_timestamp, abs=10)

    def test__get_product__invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product("invalid id")

    def test__get_products(self, client):
        response = client.get_products(take=1, continuationToken=None, returnCount=True)

        assert response.total_count is not None
        assert len(response.products) == 1
        assert response.continuation_token is not None

    def test__get_products__without_return_count(self, client):
        with pytest.raises(ValidationError) as exc_info:
            client.get_products(take=1, continuationToken=None, returnCount=False)

        assert "totalCount" in str(exc_info)

    def test__query_product(self, client):
        first_page_response = client.query_products(
            models.ProductsAdvancedQuery(
                returnCount=True,
                take=1,
                filter=FILTER,
            )
        )

        assert len(first_page_response.products) == 1
        assert first_page_response.continuation_token is not None
        assert first_page_response.total_count is not None

        continuation_token = first_page_response.continuation_token

        second_page_response = client.query_products(
            models.ProductsAdvancedQuery(
                returnCount=True,
                filter=FILTER,
                continuationToken=continuation_token,
            )
        )

        assert len(second_page_response.products) == 2
        assert second_page_response.total_count is not None

    def test__delete_product(self, client):
        product_details = models.ProductRequestObject(
            partNumber="Test_4",
            name="TestProduct_4",
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

    def test__detele_products(self, client):
        ids = []
        for part_no in range(4, 6):
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

    def test__update_products(self, client, create_test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[1].products[0].id,
            name="Updated_TestProduct_2",
            family=FAMILY,
            keywords=["UpdatedKeyword"],
            properties={"UpdatedKey": "UpdatedValue"},
            fileIds=["UpdatedTestID"],
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

        invalid_product = models.ProductUpdateRequestObject(id="invalid id")

        request_body = models.CreateProductUpdateRequest(
            products=[updated_product, invalid_product], replace=False
        )
        with pytest.raises(ValidationError) as exc_info:
            client.update_products(request_body)

        assert "failed" in str(exc_info)
        assert "error" in str(exc_info)

    def test__query_product_values(self, client):
        request_body = models.ProductValuesQuery(
            field="PART_NUMBER",
            filter="family == @0",
            substitutions=[FAMILY],
            startsWith="T",
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 3
