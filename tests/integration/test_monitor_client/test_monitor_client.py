"""This file contains the test functions for products APIs of TestMonitorClient"""
# Python Modules
import json
from datetime import datetime

# Third party modules
import pytest
from pydantic import ValidationError

# Relative Modules
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClient, models


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
def test_products(create_product):
    """Fixture to create a set of test products."""
    ids = []
    for part_no in range(1, 3):
        product_details = models.ProductRequestObject(
            partNumber=f"Test_{part_no}",
            name=f"TestProduct_{part_no}",
            family="AravindsTest",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )

        request_body = models.CreateProductsRequest(products=[product_details])
        response = json.loads(create_product(request_body).json())

        ids.append(response["products"][0]["id"])

    return ids


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClient:
    def test__api_info__returns(self, client):
        response = client.api_info()
        assert len(response.json()) != 0

    def test__create_products(self, create_product):
        product_details_3 = models.ProductRequestObject(
            partNumber="Test_3",
            name="TestProduct_3",
            family="AravindsTest",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )

        request_body = models.CreateProductsRequest(products=[product_details_3])
        response = json.loads(create_product(request_body).json())

        assert len(response["products"]) == 1

    def test__create_products__partial_success(self, create_product):
        duplicate_product_details = models.ProductRequestObject(
            partNumber="Test_3",
            name="TestProduct_3",
            family="AravindsTest",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )
        request_body = models.CreateProductsRequest(products=[duplicate_product_details])
        with pytest.raises(ValidationError) as exc_info:
            response = json.loads(create_product(request_body).json())
        assert "error" in str(exc_info)
        assert "failed" in str(exc_info)

    def test__get_product(self, client, test_products):
        product_details_response = json.loads(client.get_product(test_products[0]).json())

        assert product_details_response["part_number"] == "Test_1"
        assert product_details_response["name"] == "TestProduct_1"
        assert product_details_response["family"] == "AravindsTest"
        assert product_details_response["keywords"] == ["TestKeyword"]
        assert product_details_response["properties"] == {"TestKey": "TestValue"}
        assert product_details_response["file_ids"] == ["TestFileID"]

        timestamp_dt = datetime.fromisoformat(product_details_response["updated_at"])
        timestamp_unix = timestamp_dt.timestamp()
        now = datetime.now().timestamp()

        assert timestamp_unix == pytest.approx(now, abs=10)

    def test__get_product__invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product("invalid product id")

    def test__get_products(self, client):
        response = json.loads(
            client.get_products(take=1, continuationToken=None, returnCount=True).json()
        )

        assert response["totalCount"] is not None
        assert len(response["products"]) == 1
        assert response["continuationToken"] is not None

    def test__get_products__without_returnCount(self, client):
        with pytest.raises(ValidationError) as exc_info:
            client.get_products(take=1, continuationToken=None, returnCount=False).json()

        assert "totalCount" in str(exc_info)

    def test__query_product(self, client):
        response = json.loads(
            client.query_products(
                models.ProductsAdvancedQuery(
                    returnCount=True,
                    take=1,
                    filter="""family==\"AravindsTest\"""",
                )
            ).json()
        )

        assert len(response["products"]) == 1
        assert response["continuationToken"] is not None
        assert response["totalCount"] is not None

        continuation_token = response["continuationToken"]

        new_response = json.loads(
            client.query_products(
                models.ProductsAdvancedQuery(
                    returnCount=True,
                    filter="""family==\"AravindsTest\"""",
                    continuationToken=continuation_token,
                )
            ).json()
        )

        assert len(new_response["products"]) == 2
        assert new_response["totalCount"] is not None

    def test__delete_product(self, client):
        product_details = models.ProductRequestObject(
            partNumber="Test_4",
            name="TestProduct_4",
            family="AravindsTest",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )
        request_body = models.CreateProductsRequest(products=[product_details])
        response = json.loads(client.create_products(request_body).json())
        id = response["products"][0]["id"]

        response = client.delete_product(id)
        assert response is None

    def test__detele_products(self, client):
        ids = []
        for part_no in range(4, 6):
            product_details = models.ProductRequestObject(
                partNumber=f"Test_{part_no}",
                name=f"TestProduct_{part_no}",
                family="AravindsTest",
                keywords=["TestKeyword"],
                properties={"TestKey": "TestValue"},
                fileIds=["TestFileID"],
            )

            request_body = models.CreateProductsRequest(products=[product_details])
            response = json.loads(client.create_products(request_body).json())
            ids.append(response["products"][0]["id"])

        request_body = models.ProductDeleteRequest(ids=ids)
        response = client.delete_products(request_body)

    def test__update_products(self, client, test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=test_products[1],
            name="Updated_TestProduct_2",
            family="AravindsTest",
            keywords=["UpdatedKeyword"],
            properties={"UpdatedKey": "UpdatedValue"},
            fileIds=["UpdatedTestID"],
        )

        request_body = models.CreateProductUpdateRequest(products=[updated_product], replace=True)
        response = client.update_products(request_body).json()

        assert response["products"][0]["name"] == "Updated_TestProduct_2"
        assert response["products"][0]["keywords"] == ["UpdatedKeyword"]
        assert response["products"][0]["properties"] == {"UpdatedKey": "UpdatedValue"}
        assert response["products"][0]["fileIds"] == ["UpdatedTestID"]

    def test__update_product__without_replacing(self, client, test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=test_products[0],
            name="Updated_TestProduct_1",
            family="AravindsTest",
            keywords=["new_keyword"],
            properties={"new_key": "new_value"},
            fileIds=["new_fileID"],
        )

        request_body = models.CreateProductUpdateRequest(products=[updated_product], replace=False)
        response = client.update_products(request_body).json()

        assert response["products"][0]["name"] == "Updated_TestProduct_1"
        assert len(response["products"][0]["keywords"]) == 2
        assert len(response["products"][0]["properties"]) == 2
        assert len(response["products"][0]["fileIds"]) == 2

    def test__update_products__partial_success(self, client, test_products):
        updated_product = models.ProductUpdateRequestObject(
            id=test_products[0],
            name="Updated_TestProduct_1",
            family="AravindsTest",
            keywords=["new_keyword_2"],
            properties={"new_key_2": "new_value_2"},
            fileIds=["new_fileID_2"],
        )

        invalid_product = models.ProductUpdateRequestObject(id="invalid_id")

        request_body = models.CreateProductUpdateRequest(
            products=[updated_product, invalid_product], replace=False
        )
        response = client.update_products(request_body).json()

        assert len(response["products"]) == 1
        assert "failed" in response

    def test__query_product_values(self, client):
        request_body = models.ProductValuesQuery(
            field="PART_NUMBER",
            filter="""family == \"AravindsTest\"""",
            substitutions=None,
            startsWith="T",
        )

        response = client.query_product_values(request_body).json()
        assert len(response) == 3
