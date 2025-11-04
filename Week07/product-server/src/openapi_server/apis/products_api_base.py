# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any
from openapi_server.models.error import Error
from openapi_server.models.product import Product
from openapi_server.models.product_create import ProductCreate
from openapi_server.models.product_update import ProductUpdate
from openapi_server.security_api import get_token_bearerAuth

class BaseProductsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseProductsApi.subclasses = BaseProductsApi.subclasses + (cls,)
    async def create_product(
        self,
        product_create: ProductCreate,
    ) -> Product:
        ...


    async def get_product(
        self,
        id: StrictInt,
    ) -> Product:
        ...


    async def replace_product(
        self,
        id: StrictInt,
        product_create: ProductCreate,
    ) -> Product:
        ...


    async def delete_product(
        self,
        id: StrictInt,
    ) -> None:
        ...


    async def update_product(
        self,
        id: StrictInt,
        product_update: ProductUpdate,
    ) -> Product:
        ...
