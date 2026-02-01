# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from epa_api.models.apple_token_exchange import AppleTokenExchange
from epa_api.models.auth_token import AuthToken
from epa_api.models.login_request import LoginRequest
from epa_api.models.user_created import UserCreated
from epa_api.models.user_registration import UserRegistration
from epa_api.security_api import get_token_BearerAuth

class BaseAuthenticationApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthenticationApi.subclasses = BaseAuthenticationApi.subclasses + (cls,)
    async def register_new_user(
        self,
        user_registration: UserRegistration,
    ) -> UserCreated:
        """Creates a user account. Users must be authenticated via email to avoid spam."""
        ...


    async def login_with_password(
        self,
        login_request: LoginRequest,
    ) -> AuthToken:
        """Returns a JWT for application access."""
        ...


    async def authenticate_with_google_web(
        self,
    ) -> None:
        """Redirects the user to Google&#39;s OAuth 2.0 server to begin authentication."""
        ...


    async def google_callback(
        self,
        code: Annotated[StrictStr, Field(description="The authorization code provided by Google.")],
        state: Annotated[Optional[StrictStr], Field(description="A state string used to prevent CSRF.")],
        error: Annotated[Optional[StrictStr], Field(description="Error message if the user denied the request.")],
    ) -> AuthToken:
        """The endpoint Google redirects to after user authorization. It exchanges the &#39;code&#39; for a Google token, identifies the user, and issues an EPA session."""
        ...


    async def authenticate_with_apple_web(
        self,
        apple_token_exchange: AppleTokenExchange,
    ) -> AuthToken:
        """Exchanges an Apple Identity Token for an EPA-issued JWT."""
        ...


    async def renew_session_token(
        self,
    ) -> AuthToken:
        """Uses a session token to generate a new short-lived access JWT."""
        ...
