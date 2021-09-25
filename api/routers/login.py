# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Dict, Optional

from aioredis.client import Redis
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud, schemas
from api.core.exceptions import (
    AuthenticationProviderMissmatch,
    AuthorizationException,
    UnAuthorizedUser,
)
from api.dependencies import get_session
from api.dependencies.auth.providers import GoogleAuthProvider
from api.dependencies.auth.schemes import (
    AuthTokenCookieBearer,
    CSRFTokenRedirectCookieBearer,
)
from api.dependencies.auth.security import create_access_token, create_auth_token
from api.dependencies.cache import get_cache
from api.schemas.user import UserCreate
from api.settings import settings

prefix = settings.API_VERSION_STR + "/login"
router = APIRouter(prefix=prefix, tags=["Login"])

csrf_token_validation = CSRFTokenRedirectCookieBearer()
auth_cookie_token_data = AuthTokenCookieBearer()


@router.get("/")
async def exchange_auth_token_for_access_cookie_token(
    request: Request,
    session: AsyncSession = Depends(get_session),
    token_data: schemas.TokenPayload = Depends(auth_cookie_token_data),
) -> Optional[schemas.AccessToken]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    user = await crud.user.get(session, id=token_data.sub)
    if user is None:
        raise UnAuthorizedUser(
            log=schemas.UnAuthorizedUserLog(
                file_name=__name__,
                function_name="exchange_auth_token_for_access_cookie_token",
                detail=f"Could not fetch user id {token_data.sub} from database",
                scheme=request["scheme"],
                method=request["method"],
                root_path=request["root_path"],
                path=request["path"],
                msg="User is not authorized",
            )
        )

    # Exchange AuthCookieToken by AccessCookieToken
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        user.id, expires_delta=access_token_expires
    )

    # Redirect the user to the home page
    redirect_url = settings.API_VERSION_STR + "/users/me"
    response = RedirectResponse(url=redirect_url)

    # Set state cookie
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token.code}", httponly=True
    )

    response.delete_cookie(key="state")
    response.delete_cookie(key="auth_token")

    return response


@router.post("/access-token", response_model=schemas.AccessToken)
async def login_access_token(
    request: Request,
    session: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Optional[schemas.AccessToken]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    user = await crud.user.authenticate(
        session, email=form_data.username, password=form_data.password
    )
    if user is None:
        raise UnAuthorizedUser(
            log=schemas.UnAuthorizedUserLog(
                file_name=__name__,
                function_name="exchange_auth_token_for_access_cookie_token",
                detail="User provided incorrect email or password",
                scheme=request["scheme"],
                method=request["method"],
                root_path=request["root_path"],
                path=request["path"],
                status_code=status.HTTP_400_BAD_REQUEST,
                msg="Incorrect email or password",
            )
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = await create_access_token(user.id, expires_delta=access_token_expires)

    return token


@router.get("/google-login", tags=["Social Login"], description="Google Oauth Login")
async def google_login(cache: Redis = Depends(get_cache)) -> Optional[RedirectResponse]:
    """Redirects the user to the external authentication pop-up
    Args:
            auth_provider: The authentication provider (i.e google-iodc)
    Returns:
            Redirect response to the external provider's auth endpoint
    """
    provider = GoogleAuthProvider(client_id=settings.GOOGLE_CLIENT_ID, cache=cache)

    params = await provider.get_request_uri()
    request_uri = params.uri
    response = RedirectResponse(url=request_uri)

    return response


@router.get("/google-login-callback")
async def google_login_callback(
    request: Request,
    _: CSRFTokenRedirectCookieBearer = Depends(csrf_token_validation),
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
) -> Optional[RedirectResponse]:
    """Callback triggered when the user logs in to Google's pop-up.
    Receives an authentication_token from Google which then
    exchanges for an access_token. The latter is used to
    gain user information from Google's userinfo_endpoint.
    Args:
            request: The incoming request as redirected by Google
    """
    code = request.query_params.get("code")

    if not code:
        raise AuthorizationException("Missing external authentication token")

    provider = GoogleAuthProvider(client_id=settings.GOOGLE_CLIENT_ID, cache=cache)

    # Authenticate token and get user's info from external provider
    external_user = await provider.get_user(
        auth_token=schemas.ExternalAuthToken(code=code)
    )

    # Get or create the internal user
    db_user = await crud.user.get_by_email(session, email=external_user.email)

    if db_user is None:
        db_user = await crud.user.create(
            session,
            obj_in=UserCreate(
                name=external_user.name,
                birth_date=datetime.now().date(),
                email=external_user.email,
                is_admin=False,
                auth_provider="GOOGLE",
            ),
        )
    elif db_user.auth_provider != "GOOGLE":
        raise AuthenticationProviderMissmatch(
            log=schemas.AuthenticationProviderLog(
                file_name=__name__,
                function_name="google_login_callback",
                event="Authentication Provider Missmatch",
                detail=f"User is already registered with {db_user.auth_provider} provider",
                scheme=request["scheme"],
                method=request["method"],
                root_path=request["root_path"],
                path=request["path"],
                status_code=status.HTTP_409_CONFLICT,
                msg=f"User is already registered with another provider, \
                please use {db_user.auth_provider} provider to log-in",
                current_provider=db_user.auth_provider,
                failed_provider="GOOGLE",
            )
        )

    auth_token = await create_auth_token(db_user.id, cache)

    # Redirect the user to the home page
    redirect_url = settings.API_VERSION_STR + "/login"
    response = RedirectResponse(url=redirect_url)

    # Set state cookie
    response.set_cookie(
        key="auth_token", value=f"Bearer {auth_token.code}", httponly=True
    )

    return response


@router.get(
    "/facebook-login", tags=["Social Login"], description="Facebook Oauth Login"
)
def facebook_login() -> Dict:
    return {"message": "This is supposed to be the Facebook login endpoint"}
