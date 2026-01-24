# coding: utf-8

from fastapi.testclient import TestClient


from typing import Any  # noqa: F401
from epa_api.models.apple_token_exchange import AppleTokenExchange  # noqa: F401
from epa_api.models.auth_token import AuthToken  # noqa: F401
from epa_api.models.login_request import LoginRequest  # noqa: F401
from epa_api.models.refresh_token_request import RefreshTokenRequest  # noqa: F401
from epa_api.models.social_token_exchange import SocialTokenExchange  # noqa: F401
from epa_api.models.user_registration import UserRegistration  # noqa: F401


def test_auth_register_post(client: TestClient):
    """Test case for auth_register_post

    Register a new user
    """
    user_registration = {"password":"password","email":"email","username":"username"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/register",
    #    headers=headers,
    #    json=user_registration,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_login_post(client: TestClient):
    """Test case for auth_login_post

    Login with email/password
    """
    login_request = {"password":"password","email":"email"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/login",
    #    headers=headers,
    #    json=login_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_social_google_post(client: TestClient):
    """Test case for auth_social_google_post

    Google OAuth2 Exchange
    """
    social_token_exchange = {"id_token":"idToken"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/social/google",
    #    headers=headers,
    #    json=social_token_exchange,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_social_apple_post(client: TestClient):
    """Test case for auth_social_apple_post

    Apple Sign-In Exchange
    """
    apple_token_exchange = {"identity_token":"identityToken","full_name":"fullName"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/social/apple",
    #    headers=headers,
    #    json=apple_token_exchange,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_refresh_post(client: TestClient):
    """Test case for auth_refresh_post

    Refresh Access Token
    """
    refresh_token_request = {"refresh_token":"refreshToken"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/refresh",
    #    headers=headers,
    #    json=refresh_token_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

