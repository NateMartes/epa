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
from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from epa_api.models.apple_token_exchange import AppleTokenExchange
from epa_api.models.auth_token import AuthToken
from epa_api.models.login_request import LoginRequest
from epa_api.models.user_created import UserCreated
from epa_api.models.user_registration import UserRegistration
from epa_api.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = epa_api.api_implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/v1/auth/register",
    responses={
        200: {"model": UserCreated, "description": "User created successfully"},
    },
    tags=["Authentication"],
    summary="Register a new user",
    response_model_by_alias=True,
)
async def register_new_user(
    user_registration: UserRegistration = Body(None, description=""),
) -> UserCreated:
    """Creates a user account. Users must be authenticated via email to avoid spam."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().register_new_user(user_registration)


@router.post(
    "/v1/auth/login",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and a session token."},
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


@router.get(
    "/v1/auth/social/web/google",
    responses={
        302: {"description": "Redirect to Google Accounts."},
    },
    tags=["Authentication"],
    summary="Initiate Google OAuth2 Flow",
    response_model_by_alias=True,
)
async def authenticate_with_google_web(
) -> None:
    """Redirects the user to Google&#39;s OAuth 2.0 server to begin authentication."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().authenticate_with_google_web()


@router.get(
    "/v1/auth/social/web/google/callback",
    responses={
        200: {"model": AuthToken, "description": "Authorize the user"},
        400: {"description": "Invalid code or state mismatch."},
        401: {"description": "Authentication failed with Google."},
    },
    tags=["Authentication"],
    summary="Google OAuth2 Callback",
    response_model_by_alias=True,
)
async def google_callback(
    code: Annotated[StrictStr, Field(description="The authorization code provided by Google.")] = Query(None, description="The authorization code provided by Google.", alias="code"),
    state: Annotated[Optional[StrictStr], Field(description="A state string used to prevent CSRF.")] = Query(None, description="A state string used to prevent CSRF.", alias="state"),
    error: Annotated[Optional[StrictStr], Field(description="Error message if the user denied the request.")] = Query(None, description="Error message if the user denied the request.", alias="error"),
) -> AuthToken:
    """The endpoint Google redirects to after user authorization. It exchanges the &#39;code&#39; for a Google token, identifies the user, and issues an EPA session."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().google_callback(code, state, error)


@router.post(
    "/v1/auth/social/web/apple",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and session token."},
    },
    tags=["Authentication"],
    summary="Apple Sign-In Exchange",
    response_model_by_alias=True,
)
async def authenticate_with_apple_web(
    apple_token_exchange: AppleTokenExchange = Body(None, description=""),
) -> AuthToken:
    """Exchanges an Apple Identity Token for an EPA-issued JWT."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().authenticate_with_apple_web(apple_token_exchange)


@router.post(
    "/v1/auth/session",
    responses={
        200: {"model": AuthToken, "description": "Successful authentication returns access and a session token."},
    },
    tags=["Authentication"],
    summary="Session Token Renewal",
    response_model_by_alias=True,
)
async def renew_session_token(
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> AuthToken:
    """Uses a session token to generate a new short-lived access JWT."""
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().renew_session_token()
