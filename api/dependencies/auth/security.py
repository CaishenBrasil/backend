# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from aioredis.client import Redis
from jose import JWTError, jwt
from passlib.pwd import genword
from pydantic.types import UUID4

from api import schemas
from api.core.exceptions import UnauthorizedUser
from api.core.security import security_context
from api.settings import settings

logger = logging.getLogger(__name__)


async def create_state_csrf_token(cache: Redis) -> schemas.CSRFToken:
    """Creates a CSRF token to mitigate CSRF attacks on redirects from
    from the Authentication provider.

    The token is added in an HTTPOnly, secure cookie on the browser
    and also passed to the Auth provider as a "state" parameter.
    When the Auth provider redirects the user back to our service,
    we check that the HTTPOnly cookie value matches the "state" value
    returned by the Auth provider. We also check that we did add this
    token in the cache at some time in the past.

    Returns:
            state_csrf_token: The csrf token
    """
    secret: str = genword(entropy="secure", charset="hex")
    code: str = security_context.hash(secret).encode("utf-8").hex()

    # Values not necessary. We only need to check for existence
    await cache.set(code, 1)

    state_csrf_token = schemas.CSRFToken(code=code)

    return state_csrf_token


async def validate_state_csrf_token(
    state_csrf_token_code: str,
    cache: Redis,
) -> Optional[bool]:
    """Checks the validity of a state token received by the redirect url,
    against the state token that the server added in the browser cookie.

    Args:
            state_csrf_token: The token code returned in the redirect url
            cache: Redis connection to fetch the auth_token key
    """
    # Also, check that we 100% cached that token in the past
    cached_token_code = await cache.get(state_csrf_token_code)

    if not cached_token_code:
        raise UnauthorizedUser("Failed to validate against cached state token")

    await cache.delete(state_csrf_token_code)

    return True


async def create_auth_token(user_id: UUID4, cache: Redis) -> schemas.AuthToken:
    """Creates a one time JWT authentication token to return to the user.
    The token is used as a key to cache the user's internal id until
    he requests for an access token when it is removed from the cache.

    Args:
            user_id: The id of the User in the internal database

    Returns:
            auth_token: The encoded JWT authentication token

    """
    expires_delta = timedelta(minutes=int(settings.AUTH_TOKEN_EXPIRE_MINUTES))

    expire = datetime.utcnow() + expires_delta

    to_encode = {"exp": expire}

    code = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

    # Add token/user pair in the cache
    await cache.set(code, str(user_id))

    auth_token = schemas.AuthToken(code=code)

    return auth_token


async def get_auth_token_data(
    auth_token: schemas.AuthToken,
    cache: Redis,
) -> Optional[schemas.TokenPayload]:
    """Checks the validity of an internal authentication token.
    If the token is valid it also checks whether there is an
    associated user in the cache, and returns it.

    Args:
            auth_token: Internal authentication token
            cache: Redis connection to fetch the auth_token key

    Returns:
            token_data: A TokenPayload object containing the user_id as a sub parameter
    """
    try:
        jwt.decode(
            auth_token.code,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise UnauthorizedUser(f"Failed to validate auth token: {exc}")

    user_id = await cache.get(auth_token.code)

    if not user_id:
        raise UnauthorizedUser(f"User {user_id} not cached")

    # Invalidate cache. Authentication token can only be used once
    await cache.delete(auth_token.code)

    token_data = schemas.TokenPayload(sub=user_id)
    return token_data


async def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> schemas.AccessToken:
    """Creates a JWT access token to return to the user.

    Args:
            subject: The data to be included in the JWT access token (usually the User ID)

    Returns:
            access_token: The encoded JWT access token
    """
    expires_delta = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    access_token = schemas.AccessToken(code=encoded_jwt, access_token=encoded_jwt)

    return access_token


async def get_access_token_data(
    access_token: schemas.AccessToken,
) -> Optional[schemas.TokenPayload]:
    """Checks the validity of an internal access token and returns it.

    Args:
            access_token: Internal access token

    Returns:
            token_data: A TokenPayload object containing the user_id as a sub parameter
    """
    try:
        payload = jwt.decode(
            access_token.code,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedUser("Missing 'sub' id from access token")

    except JWTError as exc:
        raise UnauthorizedUser(f"Failed to validate access token: {exc}")

    token_data = schemas.TokenPayload(sub=user_id)
    return token_data
