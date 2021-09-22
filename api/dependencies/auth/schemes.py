# -*- coding: utf-8 -*-
from typing import Optional

from aioredis.client import Redis
from fastapi import Request, status
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from api import schemas
from api.core.exceptions import UnAuthorizedUser, exception_handling
from api.dependencies.cache import get_cache
from api.settings import settings

from .security import (
    get_access_token_data,
    get_auth_token_data,
    validate_state_csrf_token,
)


class CSRFTokenRedirectCookieBearer:
    """Scheme that checks the validity of the state parameter
    returned by the Authentication provider when it redirects
    the user to the application after a successful sing in.
    """

    async def __call__(
        self, request: Request, cache: Redis = Depends(get_cache)
    ) -> Optional[bool]:
        async with exception_handling():
            # State token from redirect
            state_csrf_token: str = request.query_params.get("state")

            return await validate_state_csrf_token(state_csrf_token, cache)


class AccessTokenCookieBearer:
    """Scheme that checks the validity of the access token
    that is stored to an HTTPOnly secure cookie in order
    to authorize the user.
    """

    async def __call__(self, request: Request) -> schemas.TokenPayload:
        async with exception_handling():
            authorization: str = request.cookies.get("access_token")
            if authorization is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Access Token Cookie is missing",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid access token cookie",
                )
                raise UnAuthorizedUser(log=log)

            scheme, code = authorization.split()
            if scheme.lower() != "bearer":
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization scheme is different from 'Bearer'",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid authorization scheme",
                )
                raise UnAuthorizedUser(log=log)

            if code is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Could not find auth_token on the Authorization header",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid auth token",
                )
                raise UnAuthorizedUser(log=log)

            access_token = schemas.AccessToken(code=code, access_token=code)

            token_data = await get_access_token_data(access_token)

            return token_data


class AccessTokenBearer(OAuth2PasswordBearer):
    """Scheme that checks the validity of the access token
    that is stored to an HTTPOnly secure cookie in order
    to authorize the user.
    """

    async def __call__(self, request: Request) -> schemas.TokenPayload:
        async with exception_handling():
            authorization: str = request.headers.get("Authorization")
            scheme, access_token_code = get_authorization_scheme_param(authorization)

            if authorization is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization header is missing",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Authorization header is missing",
                )
                raise UnAuthorizedUser(log=log)

            if scheme.lower() != "bearer":
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization scheme is different from 'Bearer'",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid authorization scheme",
                )
                raise UnAuthorizedUser(log=log)

            if access_token_code is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Could not find access_token on the Authorization header",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid access token",
                )
                raise UnAuthorizedUser(log=log)

            # Remove Bearer
            code = access_token_code.split()[1]
            access_token = schemas.AccessToken(code=code, access_token=code)

            token_data = await get_access_token_data(access_token)

            return token_data


class AccessTokenValidator:
    """Scheme that checks the validity of the access token
    that is stored either to an HTTPOnly secure cookie
    or on a Authorization header.
    """

    async def __call__(self, request: Request) -> schemas.TokenPayload:
        token_url = settings.API_VERSION_STR + "/login/access-token"

        async with exception_handling():
            authorization: str = request.headers.get("Authorization")
            if authorization:
                get_token_data = AccessTokenBearer(tokenUrl=token_url)
                token_data = await get_token_data(request)
                return token_data
            else:
                get_cookie_token_data = AccessTokenCookieBearer()
                token_data = await get_cookie_token_data(request)
                return token_data


class AuthTokenBearer:
    """Scheme that checks the validity of the authorization token
    that is exchanged prior to authenticating the user in the
    service and issuing the final access token.
    """

    async def __call__(
        self, request: Request, cache: Redis = Depends(get_cache)
    ) -> schemas.TokenPayload:
        async with exception_handling():
            authorization: str = request.headers.get("Authorization")
            scheme, auth_token = get_authorization_scheme_param(authorization)

            if authorization is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization header is missing",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Authorization header is missing",
                )
                raise UnAuthorizedUser(log=log)

            if scheme.lower() != "bearer":
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization scheme is different from 'Bearer'",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid authorization scheme",
                )
                raise UnAuthorizedUser(log=log)

            if auth_token is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Could not find auth_token on the Authorization cookie",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid auth token",
                )
                raise UnAuthorizedUser(log=log)

            auth_token = schemas.AuthToken(code=auth_token)
            token_data = await get_auth_token_data(
                auth_token=auth_token,
                cache=cache,
            )

            return token_data


class AuthTokenCookieBearer:
    """Scheme that checks the validity of the auth token
    that is stored to an HTTPOnly secure cookie.
    """

    async def __call__(
        self, request: Request, cache: Redis = Depends(get_cache)
    ) -> schemas.TokenPayload:
        async with exception_handling():
            authorization: str = request.cookies.get("auth_token")
            if authorization is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization Token Cookie is missing",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid auth token",
                )
                raise UnAuthorizedUser(log=log)

            scheme, code = authorization.split()
            if scheme.lower() != "bearer":
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Authorization Token Cookie is missing",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid auth token",
                )
                raise UnAuthorizedUser(log=log)

            if code is None:
                log = schemas.UnAuthorizedUserLog(
                    file_name=__name__,
                    class_name=type(self).__name__,
                    detail="Could not find auth_token on the Authorization cookie",
                    request=request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Invalid auth token",
                )
                raise UnAuthorizedUser(log=log)

            auth_token = schemas.AuthToken(code=code)

            token_data = await get_auth_token_data(auth_token=auth_token, cache=cache)

            return token_data
