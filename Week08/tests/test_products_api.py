# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.product import Product  # noqa: F401
from openapi_server.models.product_create import ProductCreate  # noqa: F401
from openapi_server.models.product_update import ProductUpdate  # noqa: F401


def test_create_product(client: TestClient):
    """Test case for create_product

    Create a product
    """
    product_create = {"price":0.8008282,"name":"name","description":"description","stock":6}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/products",
    #    headers=headers,
    #    json=product_create,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_product(client: TestClient):
    """Test case for get_product

    Get product by ID
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/products/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_replace_product(client: TestClient):
    """Test case for replace_product

    Replace product
    """
    product_create = {"price":0.8008282,"name":"name","description":"description","stock":6}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/products/{id}".format(id=56),
    #    headers=headers,
    #    json=product_create,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_product(client: TestClient):
    """Test case for delete_product

    Delete product
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/products/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_product(client: TestClient):
    """Test case for update_product

    Update product partially
    """
    product_update = {"price":0.8008282,"name":"name","description":"description","stock":6}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/products/{id}".format(id=56),
    #    headers=headers,
    #    json=product_update,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

