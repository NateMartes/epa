# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import Any
from epa_api.models.apple_token_exchange import AppleTokenExchange
from epa_api.models.auth_token import AuthToken
from epa_api.models.login_request import LoginRequest
from epa_api.models.refresh_token_request import RefreshTokenRequest
from epa_api.models.social_token_exchange import SocialTokenExchange
from epa_api.models.user_registration import UserRegistration


class BaseAuthenticationApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthenticationApi.subclasses = BaseAuthenticationApi.subclasses + (cls,)
    async def register_new_user(
        self,
        user_registration: UserRegistration,
    ) -> None:
        """Creates a user account. Users must be authenticated via email to avoid spam."""
        ...


    async def login_with_password(
        self,
        login_request: LoginRequest,
    ) -> AuthToken:
        """Returns a JWT for application access."""
        ...


    async def authenticate_with_google(
        self,
        social_token_exchange: SocialTokenExchange,
    ) -> AuthToken:
        """Exchanges a Google ID Token for an EPA-issued JWT."""
        ...


    async def authenticate_with_apple(
        self,
        apple_token_exchange: AppleTokenExchange,
    ) -> AuthToken:
        """Exchanges an Apple Identity Token for an EPA-issued JWT."""
        ...


    async def refresh_session_token(
        self,
        refresh_token_request: RefreshTokenRequest,
    ) -> AuthToken:
        """Uses a refresh token to generate a new short-lived access JWT."""
        ...
