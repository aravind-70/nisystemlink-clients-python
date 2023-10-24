# Python Modules
import json
from datetime import datetime

# Third party modules
import pytest

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
    for part_no in range(1, 2):
        product_details = models.ProductRequest(
            partNumber=f"Test_{part_no}",
            name="TestProduct",
            family="Test",
            keywords=["TestKeyword"],
            properties={"TestKey": "TestValue"},
            fileIds=["TestFileID"],
        )

        request_body = models.CreateProductRequest(products=[product_details])
        response = json.loads(create_product(request_body).json())

        ids.append(response['products'][0]['id'])

    return ids


@pytest.mark.enterprise
@pytest.mark.integration
class TestSuiteTestMonitorClient:
    def test__api_info__returns(self, client):
        response = client.api_info()
        assert len(response.json()) != 0

    def test__create_product(self, client, test_products):

        product_details = json.loads(client.get_product(test_products[0]).json())
        assert product_details['partNumber'] == 'Test_1'
        assert product_details['name'] == 'TestProduct'
        assert product_details['family'] == 'Test'
        assert product_details['keywords'] == ['TestKeyword']
        assert product_details['properties'] == {'TestKey': 'TestValue'}
        assert product_details['fileIds'] == ['TestFileID']

        timestamp_dt = datetime.fromisoformat(product_details['updatedAt'])
        timestamp_unix = timestamp_dt.timestamp()
        now = datetime.now().timestamp()
        assert timestamp_unix == pytest.approx(now, abs=10)

    def test__get_product_invalid_id(self, client):
        with pytest.raises(ApiException, match="404 Not Found"):
            client.get_product("invalid product id")

    # def test__query_product__all(self, client):
    #     query_filter = models.ProductsAdvancedQuery(
    #         filter=None,
    #         substitutions=None,
    #         orderBy=None,
    #         descending=False,
    #         projection=None,
    #         take=1000,
    #         continuationToken=None,
    #         returnCount=True,
    #     )
    #     response = json.loads(client.query_products(query_filter).json())
    #     assert len(response) != 0
    #     assert response["continuationToken"] is not None

    # def test__query_product__one(self, client):
    #     query_filter = models.ProductsAdvancedQuery(returnCount=True)
    #     response = json.loads(client.query_products(query_filter).json())
    #     assert len(response) != 0
    #     assert response["continuationToken"] is not None
    #     assert response["totalCount"] is not None
