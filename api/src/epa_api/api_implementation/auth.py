"""
Service Methods for API Auth Endpoints

Functions are called here if their name is specified as
an operationId in the OpenAPI specification.
"""

from fastapi.exceptions import HTTPException
from epa_api.apis.authentication_api_base import BaseAuthenticationApi
from epa_api.models.user_registration import UserRegistration
from fastapi import status
import pymongo

class AuthAPIImplementation(BaseAuthenticationApi):
    async def register_new_user(self, user_registration: UserRegistration):
        
        # Verify that payload is valid for user registration
        if not user_registration or not user_registration.validate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            
        