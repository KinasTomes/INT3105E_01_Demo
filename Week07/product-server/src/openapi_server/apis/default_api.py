# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
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
from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from openapi_server.models.error import Error
from openapi_server.models.product_list_response import ProductListResponse
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/products",
    responses={
        200: {"model": ProductListResponse, "description": "OK"},
        401: {"model": Error, "description": "Unauthorized"},
    },
    tags=["default"],
    summary="List products in page",
    response_model_by_alias=True,
)
async def list_products(
    page: Optional[Annotated[int, Field(strict=True, ge=1)]] = Query(1, description="", alias="page", ge=1),
    page_size: Optional[Annotated[int, Field(le=50, strict=True, ge=1)]] = Query(20, description="", alias="pageSize", ge=1, le=50),
    q: Annotated[Optional[StrictStr], Field(description="Optional name/keyword search")] = Query(None, description="Optional name/keyword search", alias="q"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ProductListResponse:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().list_products(page, page_size, q)
