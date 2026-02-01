from typing import Dict, Any
import requests
import os

class GoogleUtils:
    """A class with helpful methods to interact with a user via Google OAuth"""
    
    @staticmethod
    def get_auth_endpoint() -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"
        
    @staticmethod
    def get_token_endpoint() -> str:
        return "https://oauth2.googleapis.com/token"
    
    @staticmethod 
    def get_userinfo_endpoint() -> str:
        return "https://www.googleapis.com/oauth2/v2/userinfo"
        
    @staticmethod
    def get_query_params_web_request() -> Dict[Any, Any]:
        
        client_id = os.getenv("EPA_GOOGLE_WEB_CLIENT_ID", None)
        redirect_url = os.getenv("EPA_GOOGLE_WEB_REDIRECT_URI", None)
        if not client_id or not redirect_url:
            raise ValueError("Environment variables for Google OAuth {EPA_GOOGLE_WEB_CLIENT_ID, EPA_GOOGLE_WEB_REDIRECT_URI} not set")
            
        response_type = "code"
        scope = "openid email profile"
        access_type = "offline"
        prompt = "consent"
        
        return {
            "client_id": client_id,
            "redirect_uri": redirect_url,
            "response_type": response_type,
            "scope": scope,
            "access_type": access_type,
            "prompt": prompt
        }
        
    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        token_url = GoogleUtils.get_token_endpoint()
        
        payload = {
            "code": code,
            "client_id": os.getenv("EPA_GOOGLE_WEB_CLIENT_ID"),
            "client_secret": os.getenv("EPA_GOOGLE_WEB_CLIENT_SECRET"),
            "redirect_uri": os.getenv("EPA_GOOGLE_WEB_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }
    
        response = requests.post(token_url, data=payload)
    
        if not response.ok:
            raise Exception(f"Google Token Exchange failed: {response.text}")
    
        return response.json()
    
    @staticmethod
    def get_google_user_info(access_token: str) -> Dict[str, Any]:

        user_info_url = GoogleUtils.get_userinfo_endpoint()
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(user_info_url, headers=headers)
        
        if not response.ok:
            raise Exception(f"Failed to fetch user info: {response.text}")
            
        return response.json()
        
        