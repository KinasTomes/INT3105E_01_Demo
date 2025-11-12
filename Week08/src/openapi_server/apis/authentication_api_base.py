# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.error import Error
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.refresh_request import RefreshRequest
from openapi_server.models.token_response import TokenResponse


class BaseAuthenticationApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthenticationApi.subclasses = BaseAuthenticationApi.subclasses + (cls,)
    async def login(
        self,
        login_request: LoginRequest,
    ) -> TokenResponse:
        """Authenticate user and receive access token and refresh token"""
        ...


    async def refresh_token(
        self,
        refresh_request: RefreshRequest,
    ) -> TokenResponse:
        """Exchange refresh token for a new access token"""
        ...
