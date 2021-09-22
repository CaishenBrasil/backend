# -*- coding: utf-8 -*-
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from aioredis.client import Redis
from fastapi import status
from oauthlib.oauth2 import WebApplicationClient

from api.core.exceptions import (
    DiscoveryDocumentError,
    ProviderConnectionError,
    UnAuthorizedUser,
    UnknownAuthenticationProvider,
)
from api.schemas import (
    AuthenticationProviderLog,
    ExternalAuthToken,
    ExternalUser,
    RequestUriParams,
    UnAuthorizedUserLog,
)
from api.settings import settings

from .security import create_state_csrf_token

logger = logging.getLogger(__name__)


class AuthProvider(ABC):
    """Authentication providers interface"""

    def __init__(self, client_id: str, cache: Redis):
        # OAuth 2 client setup
        self.auth_client = WebApplicationClient(client_id)
        self.cache = cache

    @staticmethod
    @abstractmethod
    async def meets_condition(auth_provider: str) -> bool:
        """Checks whether this type of authentication provider
        matches any of the ones defined in the settings configuration.

        Makes sure the correct provider will be instantiated.
        """
        ...

    @abstractmethod
    async def get_user(self, auth_token: ExternalAuthToken) -> ExternalUser:
        """Receives an authentication token from an external provider (i.e Google, Microsoft)
        and exchanges it for an access token. Then, it retrieves the user's details from
        the external providers user-info endpoint.

        Args:
                auth_token: The authentication token received from the external provider

        Returns:
                external_user: A user object with the details of the user's account as
                                                it is stored in the external provider's system.
        """
        ...

    @abstractmethod
    async def get_request_uri(self) -> RequestUriParams:
        """Returns the external provider's URL for sign in and the CSRF State token.

        For example, for Google this will be a URL that will
        bring up the Google sign in pop-up window and prompt
        the user to log-in.

        Returns:
                request_uri_params: Sign in pop-up URL and CSRF State Token
        """
        ...

    @abstractmethod
    async def _get_discovery_document(self) -> dict:
        """Returns the OpenId settingsuration information from the Auth provider.

        This is handy in order to get the:
                1. token endpoint
                2. authorization endpoint
                3. user info endpoint

        Returns:
                discovery_document: The settings configuration dictionary
        """
        ...


class GoogleAuthProvider(AuthProvider):
    """Google authentication class for authenticating users and
    requesting user's information via an OpenIdConnect flow.
    """

    @staticmethod
    async def meets_condition(auth_provider: str) -> bool:
        return auth_provider == settings.GOOGLE

    async def get_user(self, auth_token: ExternalAuthToken) -> ExternalUser:
        # Get Google's endpoints from discovery document
        discovery_document = await self._get_discovery_document()
        try:
            token_endpoint = discovery_document["token_endpoint"]
            userinfo_endpoint = discovery_document["userinfo_endpoint"]
        except KeyError as exc:
            raise DiscoveryDocumentError(
                log=AuthenticationProviderLog(
                    file_name=__name__,
                    class_name=type(self).__class__,
                    function_name="get_user",
                    detail=f"Could not parse Google's discovery document: {repr(exc)}",
                    msg="Could not parse Google's discovery document",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            )

        # Request access_token from Google
        token_url, headers, body = self.auth_client.prepare_token_request(
            token_endpoint,
            redirect_url=settings.GOOGLE_REDIRECT_URL,
            code=auth_token.code,
        )

        try:
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    token_url,
                    headers=headers,
                    data=body,
                    auth=(settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET),
                )

                self.auth_client.parse_request_body_response(
                    json.dumps(token_response.json())
                )

        except Exception as exc:
            raise ProviderConnectionError(
                log=AuthenticationProviderLog(
                    file_name=__name__,
                    class_name=type(self).__class__,
                    function_name="get_user",
                    detail=f"Could not get Google's access token: {repr(exc)}",
                    msg="Could not get Google's access token",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            )

        # Request user's information from Google
        uri, headers, body = self.auth_client.add_token(userinfo_endpoint)
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(uri, headers=headers)
            userinfo = userinfo_response.json()

        if userinfo.get("email_verified") is None:
            raise UnAuthorizedUser(
                log=UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__class__,
                    function_name="get_user",
                    detail="User's email is not verified by Google",
                    msg="User account not verified by Google.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            )
        else:
            external_user = ExternalUser(
                email=userinfo["email"],
                name=userinfo["name"],
                sub=userinfo["sub"],
            )

            return external_user

    async def get_request_uri(self) -> RequestUriParams:
        discovery_document = await self._get_discovery_document()

        try:
            authorization_endpoint = discovery_document["authorization_endpoint"]
        except KeyError as exc:
            raise ProviderConnectionError(
                log=AuthenticationProviderLog(
                    file_name=__name__,
                    class_name=type(self).__class__,
                    function_name="get_request_uri",
                    detail=f"Could not parse Google's discovery document: {repr(exc)}",
                    msg="Could not parse Google's discovery document",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            )

        state_csrf_token = await create_state_csrf_token(self.cache)

        request_uri = self.auth_client.prepare_request_uri(
            authorization_endpoint,
            state=state_csrf_token.code,
            redirect_uri=settings.GOOGLE_REDIRECT_URL,
            scope=["openid", "email", "profile"],
        )

        request_uri_params = RequestUriParams(state=state_csrf_token, uri=request_uri)

        return request_uri_params

    async def _get_discovery_document(self) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.GOOGLE_DISCOVERY_URL)
                discovery_document = response.json()
        except Exception as exc:
            raise ProviderConnectionError(
                log=AuthenticationProviderLog(
                    file_name=__name__,
                    class_name=type(self).__class__,
                    function_name="_get_discovery_document",
                    detail=f"Could not get Google's discovery document: {repr(exc)}",
                    msg="Could not get Google's discovery document",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            )

        return discovery_document


async def get_auth_provider(auth_provider: str) -> Optional[AuthProvider]:
    """Works out the correct authentication provider that needs
    to be contacted, based on the provider name that was
    passed as an argument.

    Raises:
            core.exceptions.UnknownAuthenticationProvider
    """
    for provider_cls in AuthProvider.__subclasses__():
        try:
            if await provider_cls.meets_condition(auth_provider):
                return provider_cls(client_id=provider_cls.client_id)  # type: ignore
        except KeyError:
            continue

    raise UnknownAuthenticationProvider(
        log=AuthenticationProviderLog(
            file_name=__name__,
            function_name="_get_discovery_document",
            detail="The authentication provider requested is not known",
            msg="The authentication provider requested is not known",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    )
