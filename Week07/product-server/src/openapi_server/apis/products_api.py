# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.products_api_base import BaseProductsApi
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
from pydantic import StrictInt
from typing import Any
from openapi_server.models.error import Error
from openapi_server.models.product import Product
from openapi_server.models.product_create import ProductCreate
from openapi_server.models.product_update import ProductUpdate
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/products",
    responses={
        201: {"model": Product, "description": "Created"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
    },
    tags=["Products"],
    summary="Create a product",
    response_model_by_alias=True,
)
async def create_product(
    product_create: ProductCreate = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Product:
    if not BaseProductsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProductsApi.subclasses[0]().create_product(product_create)


@router.get(
    "/products/{id}",
    responses={
        200: {"model": Product, "description": "OK"},
        401: {"model": Error, "description": "Unauthorized"},
        404: {"model": Error, "description": "Not Found"},
    },
    tags=["Products"],
    summary="Get product by ID",
    response_model_by_alias=True,
)
async def get_product(
    id: StrictInt = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Product:
    if not BaseProductsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProductsApi.subclasses[0]().get_product(id)


@router.put(
    "/products/{id}",
    responses={
        200: {"model": Product, "description": "OK"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        404: {"model": Error, "description": "Not Found"},
    },
    tags=["Products"],
    summary="Replace product",
    response_model_by_alias=True,
)
async def replace_product(
    id: StrictInt = Path(..., description=""),
    product_create: ProductCreate = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Product:
    if not BaseProductsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProductsApi.subclasses[0]().replace_product(id, product_create)


@router.delete(
    "/products/{id}",
    responses={
        204: {"description": "No Content"},
        401: {"model": Error, "description": "Unauthorized"},
        404: {"model": Error, "description": "Not Found"},
    },
    tags=["Products"],
    summary="Delete product",
    response_model_by_alias=True,
)
async def delete_product(
    id: StrictInt = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseProductsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProductsApi.subclasses[0]().delete_product(id)


@router.patch(
    "/products/{id}",
    responses={
        200: {"model": Product, "description": "OK"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        404: {"model": Error, "description": "Not Found"},
    },
    tags=["Products"],
    summary="Update product partially",
    response_model_by_alias=True,
)
async def update_product(
    id: StrictInt = Path(..., description=""),
    product_update: ProductUpdate = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Product:
    if not BaseProductsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProductsApi.subclasses[0]().update_product(id, product_update)
