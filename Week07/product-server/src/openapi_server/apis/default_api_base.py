# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from openapi_server.models.error import Error
from openapi_server.models.product_list_response import ProductListResponse
from openapi_server.security_api import get_token_bearerAuth

class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def list_products(
        self,
        page: Optional[Annotated[int, Field(strict=True, ge=1)]],
        page_size: Optional[Annotated[int, Field(le=50, strict=True, ge=1)]],
        q: Annotated[Optional[StrictStr], Field(description="Optional name/keyword search")],
    ) -> ProductListResponse:
        ...
