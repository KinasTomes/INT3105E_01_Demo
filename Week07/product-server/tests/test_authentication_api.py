# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.login_request import LoginRequest  # noqa: F401
from openapi_server.models.refresh_request import RefreshRequest  # noqa: F401
from openapi_server.models.token_response import TokenResponse  # noqa: F401


def test_login(client: TestClient):
    """Test case for login

    User login
    """
    login_request = {"password":"admin123","username":"admin"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/login",
    #    headers=headers,
    #    json=login_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_refresh_token(client: TestClient):
    """Test case for refresh_token

    Refresh access token
    """
    refresh_request = {"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/refresh",
    #    headers=headers,
    #    json=refresh_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

