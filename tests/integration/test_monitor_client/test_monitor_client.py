# Python Modules
import json
from datetime import datetime

# Third party modules
import pytest

# Relative Modules
from nisystemlink.clients.core import ApiException
from nisystemlink.clients.testmonitor import TestMonitorClient, models


# @pytest.fixture(scope="class")
def client(enterprise_config):
    return TestMonitorClient(enterprise_config)

request_body =  models.ProductRequest(
                    partNumber="test_1",
                    name="cRIO-9030",
                    family="cRIO",
                    keywords=[
                        "keyword",
                    ],
                    properties={"key1": "value1"},
                    fileIds=["5ccb19ce5aa0a3348872c3e3"],
                )
response = TestMonitorClient().create_products(request_body)

print(response.json())

@pytest.fixture(scope="class")
def create_product(client):
    products = []

    def _create_product(product):
        response = json.loads(client.create_products(product).json())
        products.append(response["id"])
        return response["id"]

    yield _create_product


@pytest.fixture(scope="class")
def test_products(create_product):
    ids = []

    for product_no in range(1, 4):
        response = create_product(
            models.CreateProductRequest(
                [
                    models.ProductRequest(
                        partNumber=f"test_{product_no}",
                        name="cRIO-9030",
                        family="cRIO",
                        keywords=[
                            "keyword",
                        ],
                        properties={"key1": "value1"},
                        fileIds=["5ccb19ce5aa0a3348872c3e3"],
                    )
                ]
            )
        )
        id = json.loads(response.json())["id"]
        ids.append(id)
    return ids


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClient:
    def test__api_info__returns(self, client):
        response = client.api_info()
        assert len(response.json()) != 0

    def test__create_product(self, client, test_products):
        product_data = json.loads(client.get_product(test_products[0]).json())
        assert product_data["partNumber"] == "test_1"
        assert product_data["name"] == "cRIO-9030"
        assert product_data["properties"] == {"key1": "value1"}

    def test__get_product_valid_id(self, client):
        response = json.loads(client.get_product("da9f4084-7871-4385-9e10-2b9a9464f062").json())
        assert "da9f4084-7871-4385-9e10-2b9a9464f062" in response["id"]

    def test__get_product_invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product("invalid product id")

    def test__query_product__all(self, client):
        query_filter = models.ProductsAdvancedQuery(
            filter=None,
            substitutions=None,
            orderBy=None,
            descending=False,
            projection=None,
            take=1000,
            continuationToken=None,
            returnCount=True,
        )
        response = json.loads(client.query_products(query_filter).json())
        assert len(response) != 0
        assert response["continuationToken"] is not None

    # def test__query_product__one(self, client):
    #     query_filter = models.ProductsAdvancedQuery(returnCount=True)
    #     response = json.loads(client.query_products(query_filter).json())
    #     assert len(response) != 0
    #     assert response["continuationToken"] is not None
    #     assert response["totalCount"] is not None
