"""Functionality of Product APIs."""
# Python module.
import logging

# Third party moduels.
from nisystemlink.clients.testmonitor import TestMonitorClient
from nisystemlink.clients.testmonitor.models import (
    CreateProductsRequest,
    ProductField,
    ProductQueryOrderByField,
    ProductRequestObject,
    ProductsAdvancedQuery,
    ProductUpdateRequestObject,
    UpdateProductsRequest,
)

# Constant.
FAMILY = "EXAMPLE FAMILY"

# Configure the logger.
logging.basicConfig(level=logging.INFO)

client = TestMonitorClient()

# Create a Product.
products_request = CreateProductsRequest(
    products=[
        ProductRequestObject(
            part_number="example_product_1",
            name="example_product",
            family=FAMILY,
            keywords=["example_keywords"],
            properties={"example_key": "example_value"},
            file_ids=["example_file_id"],
        )
    ]
)
example_product = client.create_products(products=products_request).products[0]
product_id = example_product.id

logging.info("Product Created Successfully.")
logging.info(f"Created Product Name: {example_product.name}")

# Update the product.
update_product_request = UpdateProductsRequest(
    products=[
        ProductUpdateRequestObject(
            id=product_id,
            name="updated_product",
            family=FAMILY,
            keywords=["updated_keywords"],
            properties={"updated_key": "updated_value"},
            file_ids=["updated_file_id"],
        )
    ],
    replace=False,
)
updated_product = client.update_products(request_body=update_product_request).products[0]

logging.info("Product Updated Successfully.")
logging.info(f"Updated Product Name: {updated_product.name}")

# Query the product.
query_filter = ProductsAdvancedQuery(
    filter="family == @0",
    substitutions=[FAMILY],
    order_by=ProductQueryOrderByField.NAME,
    descending=False,
    projection=[ProductField.NAME],
    take=1,
    continuation_token=None,
    return_count=True,
)
queried_product = client.query_products(query_filter=query_filter).products[0]

logging.info("Product Queried Successfully.")
logging.info(f"Queried Product Name: {queried_product.name}")

# Delete the product.
client.delete_product(productId=product_id)
logging.info("Product Deleted Successfully")
