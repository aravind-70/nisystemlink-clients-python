"""This file contains the test functions for products APIs of TestMonitor."""
# Python Modules
from datetime import datetime

# Third party modules
import pytest
from pydantic import ValidationError

# Relative Modules
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClientProducts, models


@pytest.fixture(scope="class")
def client(enterprise_config):
    """Fixture to create a TestMonitorClient instance."""
    return TestMonitorClientProducts(enterprise_config)


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
            family="TestProductsApi",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )

        request_body = models.CreateProductsRequest(products=[product_details])
        response = create_product(request_body)

        sample_test_products.append(response.products[0].id)

    return sample_test_products


@pytest.fixture(scope="class")
def product_request_body():
    product_request_object = models.ProductRequestObject(
        partNumber="TestProduct",
        name="TestProduct_3",
        family="TestProductsApi",
        keywords=["TestKeyword"],
        properties={"TestKey": "TestValue"},
        fileIds=["TestFileID"],
    )
    request_body = models.CreateProductsRequest(products=[product_request_object])

    return request_body


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClientProducts:
    def test__create_products(self, create_product, product_request_body):
        response = create_product(product_request_body)
        assert len(response.products) == 1

    def test__create_products__partial_success(self, create_product, product_request_body):
        with pytest.raises(ValidationError) as exc_info:
            create_product(product_request_body)

        assert "error" in str(exc_info)
        assert "failed" in str(exc_info)

    def test__get_product(self, client, create_test_products):
        product_details = client.get_product(create_test_products[0])

        assert product_details.part_number == "Test_1"
        assert product_details.name == "TestProduct_1"
        assert product_details.family == "TestProductsApi"
        assert product_details.keywords == ["TestKeyword"]
        assert product_details.properties == {"TestKey": "TestValue"}
        assert product_details.file_ids == ["TestFileID"]

        updated_at_timestamp = product_details.updated_at.timestamp()
        now = datetime.now().timestamp()

        assert updated_at_timestamp == pytest.approx(now, abs=10)

    def test__get_product__invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product("invalid id")

    def test__get_products(self, client):
        response = client.get_products(take=1, continuationToken=None, returnCount=True)

        assert response.total_count is not None
        assert len(response.products) == 1
        assert response.continuation_token is not None

    def test__get_products__without_returnCount(self, client):
        with pytest.raises(ValidationError) as exc_info:
            client.get_products(take=1, continuationToken=None, returnCount=False)

        assert "totalCount" in str(exc_info)

    def test__query_product(self, client):
        response = client.query_products(
            models.ProductsAdvancedQuery(
                returnCount=True,
                take=1,
                filter="""family==\"TestProductsApi\"""",
            )
        )

        assert len(response.products) == 1
        assert response.continuation_token is not None
        assert response.total_count is not None

        continuation_token = response.continuation_token

        new_response = client.query_products(
            models.ProductsAdvancedQuery(
                returnCount=True,
                filter="""family==\"TestProductsApi\"""",
                continuationToken=continuation_token,
            )
        )

        assert len(new_response.products) == 2
        assert new_response.total_count is not None

    def test__delete_product(self, client):
        product_details = models.ProductRequestObject(
            partNumber="Test_4",
            name="TestProduct_4",
            family="TestProductsApi",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
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
                family="TestProductsApi",
                keywords=["TestKeyword"],
                properties={"TestKey": "TestValue"},
                fileIds=["TestFileID"],
            )

            request_body = models.CreateProductsRequest(products=[product_details])
            response = client.create_products(request_body)
            ids.append(response.products[0].id)

        request_body = models.ProductDeleteRequest(ids=ids)
        response = client.delete_products(request_body)
        assert response is None

    def test__update_products(self, client, create_test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[1],
            name="Updated_TestProduct_2",
            family="TestProductsApi",
            keywords=["UpdatedKeyword"],
            properties={"UpdatedKey": "UpdatedValue"},
            fileIds=["UpdatedTestID"],
        )

        request_body = models.CreateProductUpdateRequest(products=[updated_product], replace=True)
        response = client.update_products(request_body)

        assert response.products[0].name == "Updated_TestProduct_2"
        assert response.products[0].keywords == ["UpdatedKeyword"]
        assert response.products[0].properties == {"UpdatedKey": "UpdatedValue"}
        assert response.products[0].file_ids == ["UpdatedTestID"]

    def test__update_products__without_replacing(self, client, create_test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[0],
            name="Updated_TestProduct_1",
            family="TestProductsApi",
            keywords=["new_keyword"],
            properties={"new_key": "new_value"},
            fileIds=["new_fileID"],
        )

        request_body = models.CreateProductUpdateRequest(products=[updated_product], replace=False)
        response = client.update_products(request_body)

        assert response.products[0].name == "Updated_TestProduct_1"
        assert len(response.products[0].keywords) == 2
        assert len(response.products[0].properties) == 2
        assert len(response.products[0].file_ids) == 2

    def test__update_products__partial_success(self, client, create_test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=create_test_products[0],
            name="Updated_TestProduct_1",
            family="TestProductsApi",
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
            substitutions=["TestProductsApi"],
            startsWith="T",
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 3
