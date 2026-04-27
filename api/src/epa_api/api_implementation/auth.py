"""
Service Methods for API Auth Endpoints

Functions are called here if their name is specified as
an operationId in the OpenAPI specification.
"""

from typing import Optional
from pydantic import StrictStr
from fastapi.exceptions import HTTPException
from epa_api.apis.authentication_api_base import BaseAuthenticationApi
from epa_api.models.user_registration import UserRegistration
from epa_api.models.user_created import UserCreated
from epa_api.models.login_request import LoginRequest
from epa_api.models.auth_token import AuthToken
from epa_api.api_implementation.utils.mongo import MongoUtils
from epa_api.api_implementation.utils.user import UserUtils
from epa_api.api_implementation.utils.token import TokenUtils
from epa_api.api_implementation.utils.google import GoogleUtils
from epa_api.models.username_response import UsernameResponse 
from fastapi.responses import RedirectResponse
from fastapi import status
import urllib.parse

class AuthAPIImplementation(BaseAuthenticationApi):
    async def register_new_user(self, user_registration: UserRegistration) -> UserCreated:
        """Creates a user account. Users must be authenticated via email to avoid spam."""
        
        # Verify that payload is valid for user registration
        if not user_registration or not user_registration.model_validate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            
        # Check that username is at least 8 characters
        if len(user_registration.username) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be at least 6 characters")
            
        # Check that password is at least 12 characters
        if len(user_registration.password) < 12:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 12 characters")
            
        # Connect to the database
        client, db = MongoUtils.get_mongodb_database_connection()
        user_collection = MongoUtils.get_user_collection(db)
        
        # Check that the creds are not taken
        if UserUtils.is_email_taken(user_registration.email, user_collection):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already taken")
        
        if UserUtils.is_username_taken(user_registration.username, user_collection):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        
        # Create the user
        user_id = UserUtils.create_standard_user(
            user_registration,
            user_collection
        )
        
        client.close()
        return UserCreated(user_id=user_id)
        
    async def login_with_password(self, login_request: LoginRequest) -> AuthToken:
        """Returns a JWT for application access."""

        # Verify that payload is valid for user login
        if not login_request.model_validate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
        email = login_request.email
        password = login_request.password
        
        client, db = MongoUtils.get_mongodb_database_connection()
        user_collection = MongoUtils.get_user_collection(db)
        
        user = UserUtils.get_user_from_email(email, user_collection)
        if not user or not UserUtils.verify_password(password, user["password"], user["salt"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        new_access_token = TokenUtils.generate_new_access_token(user, user_collection)
        new_session_token = TokenUtils.generate_new_session_token(user, MongoUtils.get_session_tokens_collection(db))
        client.close()
        
        expire_time = TokenUtils.get_expire_date(new_access_token)
        if not expire_time:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return AuthToken(
            access_token=new_access_token,
            session_token=new_session_token,
            token_type="Bearer",
            access_expires_in=TokenUtils.get_ttl_in_seconds(expire_time)
        )
        
    async def renew_session_token(self) -> AuthToken:
        """Uses a session token to generate a new short-lived access JWT."""

        token = TokenUtils.validate_session_token_with_db()
            
        # Make sure this session token was not invalidated early
        client, db = MongoUtils.get_mongodb_database_connection()
        session_token_collection = MongoUtils.get_session_tokens_collection(db)
        if not TokenUtils.is_session_token_in_db(token, session_token_collection):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Session")
            
        user_collection = MongoUtils.get_user_collection(db)
        user_id = TokenUtils.get_user_id(token)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        new_access_token = TokenUtils.generate_new_access_token(user, user_collection)
        client.close()
        
        expire_time = TokenUtils.get_expire_date(new_access_token)
        if not expire_time:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        return AuthToken(
            access_token=new_access_token,
            session_token=token,
            token_type="Bearer",
            access_expires_in=TokenUtils.get_ttl_in_seconds(expire_time)
        )        
        
    async def authenticate_with_google_web(self):
        """Redirects the user to Google&#39;s OAuth 2.0 server to begin authentication."""

        # This will show errors since the open api generator cannot handle redirects
        
        # Send user to google login
        url = f"{GoogleUtils.get_auth_endpoint()}?{urllib.parse.urlencode(GoogleUtils.get_query_params_web_request())}"
        return RedirectResponse(url)
        
    async def google_callback(self, code: StrictStr, state: Optional[StrictStr], error: Optional[StrictStr]) -> AuthToken:
        """The endpoint Google redirects to after user authorization. It exchanges the &#39;code&#39; for a Google token, identifies the user, and issues an EPA session."""

        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Termination code missing")
    
        # Get the user's information
        token_data = GoogleUtils.exchange_code_for_token(code)
        user_info = GoogleUtils.get_google_user_info(token_data["access_token"])
        
        # Connect to the database
        client, db = MongoUtils.get_mongodb_database_connection()
        user_collection = MongoUtils.get_user_collection(db)
                
        # Get the user's information on EPA, creating the user if they do not exist
        user_object = UserUtils.get_user_from_google_id(user_info["id"], user_collection)
        if not user_object:
            user_id = UserUtils.create_google_user(user_info, user_collection)
            user_object = UserUtils.get_user_from_user_id(user_id, user_collection)
        if user_object is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user after creation.")
            
        # Authorize the user with a session token
        new_access_token = TokenUtils.generate_new_access_token(user_object, user_collection)
        new_session_token = TokenUtils.generate_new_session_token(user_object, MongoUtils.get_session_tokens_collection(db))
        client.close()
        
        expire_time = TokenUtils.get_expire_date(new_access_token)
        if not expire_time:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        return AuthToken(
            access_token=new_access_token,
            session_token=new_session_token,
            token_type="Bearer",
            access_expires_in=TokenUtils.get_ttl_in_seconds(expire_time)
        )    
    
    async def get_username_by_user_id(
        self, 
        user_id: StrictStr
    ) -> UsernameResponse:
        
        print(user_id)
        
        TokenUtils.validate_access_token_with_db()
        
        # Connect to the database
        client, db = MongoUtils.get_mongodb_database_connection()
        user_collection = MongoUtils.get_user_collection(db)
        
        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        print(user)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        output = UsernameResponse(username=user["username"])
        return output