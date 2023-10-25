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
    return TestMonitorClient(enterprise_config)


@pytest.fixture(scope="class")
def create_product(client):
    products = []

    def _create_product(product):
        id = client.create_products(product)
        products.append(id)
        return id

    yield _create_product
    return


@pytest.fixture(scope="class")
def test_products(create_product):
    ids = []
    for part_no in range(1, 3):
        product_details = models.ProductRequest(
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

    def test__create_product(self, client, test_products):
        product_details_response = json.loads(client.get_product(test_products[0]).json())
        assert product_details_response["partNumber"] == "Test_1"
        assert product_details_response["name"] == "TestProduct_1"
        assert product_details_response["family"] == "AravindsTest"
        assert product_details_response["keywords"] == ["TestKeyword"]
        assert product_details_response["properties"] == {"TestKey": "TestValue"}
        assert product_details_response["fileIds"] == ["TestFileID"]

        timestamp_dt = datetime.fromisoformat(product_details_response["updatedAt"])
        timestamp_unix = timestamp_dt.timestamp()
        now = datetime.now().timestamp()
        assert timestamp_unix == pytest.approx(now, abs=10)

    def test__create_product_partial_success(self, create_product):
        product_details_3 = models.ProductRequest(
            partNumber="Test_3",
            name="TestProduct_3",
            family="AravindsTest",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )
        duplicate_product_details = models.ProductRequest(
            partNumber="Test_3",
            name="TestProduct_3",
            family="AravindsTest",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )

        request_body = models.CreateProductsRequest(
            products=[product_details_3, duplicate_product_details]
        )
        response = json.loads(create_product(request_body).json())

        assert len(response["products"]) == 1

    def test__get_product_invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product("invalid product id")

    def test__get_products(self, client):
        response = json.loads(
            client.get_products(take=1, continuationToken=None, returnCount=True).json()
        )
        assert response["totalCount"] is not None
        assert len(response["products"]) == 1
        assert response["continuationToken"] is not None

    def test__get_products_without_returnCount(self, client):
        with pytest.raises(ValidationError) as exc_info:
            response = json.loads(
                client.get_products(take=1, continuationToken=None, returnCount=False).json()
            )

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

    def test__delete_products(self, client):
        ids = []
        for part_no in range(4, 6):
            product_details = models.ProductRequest(
                partNumber=f"Test_{part_no}",
                name=f"TestProduct_{part_no}",
                family="AravindsTest",
                keywords=["TestKeyword"],
                properties={"TestKey": "TestValue"},
                fileIds=["TestFileID"]
            )
            request_body = models.CreateProductsRequest(products=[product_details])
            response = json.loads(client.create_products(request_body).json())
            ids.append(response['products'][0]['id'])

        for id in ids:
            response = client.delete_product(id)
            assert response is None
