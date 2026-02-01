from operator import le
from pydantic_core.core_schema import int_schema
from pymongo.collection import Collection
from datetime import datetime, timedelta
from typing import Dict, Any, List
import jwt
import os

class TokenUtils:
    """A class with helpful methods to interact with API JWT Tokens"""
            
    @staticmethod
    def is_access_token_in_db(token: str, user_collection: Collection) -> bool:
        """
        Checks if the current access token is in the database.
        This is used to handle if a user creates a new access token, invalidating previous ones.
        
        :param token: The access token to look for.
        :type token: str
        :param session_token_collection: The collection of session tokens
        :type session_token_collection: pymongo.collection.Collection
        :return: True if and only if the session token is in the database
        :rtype: bool       
        """
        
        # Access tokens only exist in one spot, with the user info.
        if user_collection.find_one({"access_token": token}):
            return True
        else:
            return False        
        
    @staticmethod
    def is_session_token_in_db(token: str, session_token_collection: Collection) -> bool:
        """
        Checks if the current session token is in the database.
        This is used to handle if a user opens mutiple session tokens, invalidating previous ones.
        
        :param token: The session token to look for
        :type token: str
        :param session_token_collection: The collection of session tokens
        :type session_token_collection: pymongo.collection.Collection
        :return: True if and only if the session token is in the database
        :rtype: bool       
        """
        
        if session_token_collection.find_one({"session_token": token}):
            return True
        else:
            return False
            
    @staticmethod       
    def get_user_session_tokens(user_id: str, session_token_collection: Collection) -> List[Dict[Any, Any]]:
        """
        Get the session tokens of a user
        
        :param user_id: The id of the user
        :type user_id: str
        :param session_token_collection: The collection of session tokens
        :type session_token_collection: pymongo.collection.Collection
        :return: A list of session token objects
        :rtype: List[Dict[Any, Any]]
        """
   
        query = {"user_id": user_id}
        cursor = session_token_collection.find(query)
        output = []
        for token_obj in cursor:
            output.append(token_obj)
            
        return output
        
    @staticmethod       
    def get_user_session_token_count(user_id: str, session_token_collection: Collection) -> int:
        """
        Get the number of session tokens the user has
        
        :param user_id: The id of the user
        :type user_id: str
        :param session_token_collection: The collection of session tokens
        :type session_token_collection: pymongo.collection.Collection
        :return: The number of session tokens
        :rtype: int
        """
   
        query = {"user_id": user_id}
        return session_token_collection.count_documents(query)
        
    @staticmethod
    def get_session_token_with_least_ttl(tokens: List[Dict[Any, Any]]) -> Dict[Any, Any] | None:
        """
        Get the session token with the least time to live (ttl), returning None if no tokens exists
        
        :param tokens: A list of session token objects
        :type tokens: List[Dict[Any, Any]]
        :return: The session token object with the least time to live (ttl)
        :rtype: List[Dict[Any, Any]]
        """        
        output = None
        least_ttl = None
        for t in tokens:
            actual_token = t["session_token"]
            ttl = TokenUtils.get_ttl_in_seconds(TokenUtils.get_expire_date(actual_token))
            if not least_ttl:
                least_ttl = ttl
                output = t
            elif ttl < least_ttl:
                least_ttl = ttl
                output = t
                
        return output
            
    @staticmethod    
    def generate_new_session_token(user: Dict[Any, Any], session_token_collection: Collection) -> str:
        """
        Gets a new session token.
    
        :param user: A user object
        :type user: Dict[Any, Any]
        :param session_token_collection: The collection of session tokens
        :type session_token_collection: pymongo.collection.Collection
        :return: A JWT token
        :rtype: str
        """
        
        # Avoid overloading of session tokens
        token_count = TokenUtils.get_user_session_token_count(user["user_id"], session_token_collection)
        if token_count > 4:
            user_session_tokens = TokenUtils.get_user_session_tokens(user["user_id"], session_token_collection)
            token_to_remove = TokenUtils.get_session_token_with_least_ttl(user_session_tokens)
            if token_to_remove:
                TokenUtils.remove_session_token(token_to_remove["session_token"], session_token_collection)
            
        new_session_token = TokenUtils.get_token({"user_id": user["user_id"]}, exp_date=(datetime.now() + timedelta(days=7)))
        session_token_collection.insert_one({
            "session_token": new_session_token,
            "user_id": user["user_id"],
            "expires_at": (datetime.now() + timedelta(days=7))
        })
        return new_session_token
        
    @staticmethod    
    def remove_session_token(token: str, session_token_collection: Collection):
        """
        Remove a session token.
    
        :param token: The session token to remove
        :type token: str
        :param session_token_collection: The collection of session tokens
        :type session_token_collection: pymongo.collection.Collection
        """
        
        result = session_token_collection.delete_one({
            "session_token": token
        })
        
        if result.deleted_count == 0:
            raise ValueError(f"Session token {token} does not exist")
        
    @staticmethod            
    def generate_new_access_token(user: Dict[Any, Any], user_collection: Collection) -> str:
        """
        Gets a new access token, invalidating the old one.
    
        :param user: A user object
        :type user: Dict[Any, Any]
        :param user_collection: The collection of users
        :type user_collection: pymongo.collection.Collection
        :return: A JWT token
        :rtype: str
        """
        new_access_token = TokenUtils.get_token({"user_id": user["user_id"]}, exp_date=(datetime.now() + timedelta(minutes=30)))
        user_collection.update_one(user, {"$set": {"access_token": new_access_token} })
        return new_access_token

    @staticmethod    
    def get_jwt_secret() -> str:
        """
        Get the JWT Secret for this API
    
        :raises ValueError if the expected env variable is not set
        :return: The JWT secret
        :rtype: str
        """
        env_var = "EPA_JWT_SECRET"
        val = os.getenv(env_var)
        if not val:
            raise ValueError("Environmnet variable EPA_JWT_SECRET not set.")
        else:
            return val
 
    @staticmethod               
    def get_token(data: Dict[Any, Any], exp_date: datetime) -> str:
        secret = TokenUtils.get_jwt_secret()
        data["exp"] = exp_date.timestamp()
        token = jwt.encode(data, secret, algorithm="HS256")
        return token
    
    @staticmethod        
    def get_expire_date(token: str) -> datetime:
        payload = TokenUtils.get_token_payload(token)
        return datetime.fromtimestamp(payload["exp"])
        
    @staticmethod        
    def get_user_id(token: str) -> str:
        payload = TokenUtils.get_token_payload(token)
        return payload["user_id"]
        
    @staticmethod        
    def get_ttl_in_seconds(date: datetime) -> int:
        time_remaining =  date - datetime.now()
        if time_remaining.microseconds < 0:
            return 0
        else:
            return time_remaining.seconds
   
    @staticmethod         
    def is_token_valid(token: str) -> bool:
        try:
            TokenUtils.get_token_payload(token)
            return True
        except jwt.DecodeError:
            return False
  
    @staticmethod              
    def get_token_payload(token: str) -> Dict[Any, Any]:
        secret = TokenUtils.get_jwt_secret()
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.DecodeError as e:
            raise e