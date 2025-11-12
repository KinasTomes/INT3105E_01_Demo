# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.authentication_api_base import BaseAuthenticationApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.models.error import Error
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.refresh_request import RefreshRequest
from openapi_server.models.token_response import TokenResponse


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/auth/login",
    responses={
        200: {"model": TokenResponse, "description": "Login successful"},
        401: {"model": Error, "description": "Invalid credentials"},
    },
    tags=["Authentication"],
    summary="User login",
    response_model_by_alias=True,
)
async def login(
    login_request: LoginRequest = Body(None, description=""),
) -> TokenResponse:
    """Authenticate user and receive access token and refresh token"""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().login(login_request)


@router.post(
    "/auth/refresh",
    responses={
        200: {"model": TokenResponse, "description": "Token refreshed successfully"},
        401: {"model": Error, "description": "Invalid or expired refresh token"},
    },
    tags=["Authentication"],
    summary="Refresh access token",
    response_model_by_alias=True,
)
async def refresh_token(
    refresh_request: RefreshRequest = Body(None, description=""),
) -> TokenResponse:
    """Exchange refresh token for a new access token"""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().refresh_token(refresh_request)
