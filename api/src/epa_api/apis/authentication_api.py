# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from epa_api.apis.authentication_api_base import BaseAuthenticationApi
import epa_api.api_implementation

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

from epa_api.models.extra_models import TokenModel  # noqa: F401
from typing import Any
from epa_api.models.apple_token_exchange import AppleTokenExchange
from epa_api.models.auth_token import AuthToken
from epa_api.models.login_request import LoginRequest
from epa_api.models.refresh_token_request import RefreshTokenRequest
from epa_api.models.social_token_exchange import SocialTokenExchange
from epa_api.models.user_registration import UserRegistration


router = APIRouter()

ns_pkg = epa_api.api_implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/v1/auth/register",
    responses={
        201: {"description": "User created successfully"},
    },
    tags=["Authentication"],
    summary="Register a new user",
    response_model_by_alias=True,
)
async def register_new_user(
    user_registration: UserRegistration = Body(None, description=""),
) -> None:
    """Creates a user account. Users must be authenticated via email to avoid spam."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().register_new_user(user_registration)


@router.post(
    "/v1/auth/login",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and refresh tokens."},
    },
    tags=["Authentication"],
    summary="Login with email/password",
    response_model_by_alias=True,
)
async def login_with_password(
    login_request: LoginRequest = Body(None, description=""),
) -> AuthToken:
    """Returns a JWT for application access."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().login_with_password(login_request)


@router.post(
    "/v1/auth/social/google",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and refresh tokens."},
    },
    tags=["Authentication"],
    summary="Google OAuth2 Exchange",
    response_model_by_alias=True,
)
async def authenticate_with_google(
    social_token_exchange: SocialTokenExchange = Body(None, description=""),
) -> AuthToken:
    """Exchanges a Google ID Token for an EPA-issued JWT."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().authenticate_with_google(social_token_exchange)


@router.post(
    "/v1/auth/social/apple",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and refresh tokens."},
    },
    tags=["Authentication"],
    summary="Apple Sign-In Exchange",
    response_model_by_alias=True,
)
async def authenticate_with_apple(
    apple_token_exchange: AppleTokenExchange = Body(None, description=""),
) -> AuthToken:
    """Exchanges an Apple Identity Token for an EPA-issued JWT."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().authenticate_with_apple(apple_token_exchange)


@router.post(
    "/v1/auth/refresh",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and refresh tokens."},
    },
    tags=["Authentication"],
    summary="Refresh Access Token",
    response_model_by_alias=True,
)
async def refresh_session_token(
    refresh_token_request: RefreshTokenRequest = Body(None, description=""),
) -> AuthToken:
    """Uses a refresh token to generate a new short-lived access JWT."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().refresh_session_token(refresh_token_request)
