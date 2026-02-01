from typing import Tuple, Dict, Any
from pydantic.types import SecretStr
from pymongo.collection import Collection
from epa_api.models.user_registration import UserRegistration
import hashlib
import uuid
import os
import binascii
import hmac

class UserUtils:
    """A class with helpful methods to interact with a user"""

    @staticmethod       
    def hash_password(password: SecretStr) -> Tuple[str, str]:
        """
        Hash a password with a random salt and PBKDF2-HMAC-SHA256.
        :param password: The password to hash
        :type password: SecretStr
        :return: The salt used to hash the password along with the hashed password
        :rtype: Tuple[str, str]
        """
        
        # Generate a random salt
        salt = os.urandom(16)
        iterations = 260000
        
        # Hash the password and the salt
        hashed_password_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.get_secret_value().encode('utf-8'),
            salt,
            iterations,
            dklen=32
        )
        
        return binascii.hexlify(salt).decode('ascii'), binascii.hexlify(hashed_password_bytes).decode('ascii')

    @staticmethod          
    def verify_password(unhashed_password: SecretStr, hashed_password: str, hashed_password_salt: str) -> bool:
        """
        Compares an unhashed password with a hashed password to see if they are the same.
        :param unhashed_password: The password to test
        :type unhashed_password: SecretStr
        :param hashed_password: The password to compare against the unhashed password
        :type hashed_password: str
        :param hashed_password_salt: The password salt that was used on the original hashed password
        :type hashed_password_salt: str
        :return: True if and only if the unhashed_password is the same has the hashed password
        :rtype: bool
        """
        iterations = 260000
        salt_bytes = binascii.unhexlify(hashed_password_salt)
        
        # Hash the provided password with the stored salt
        new_hashed_password = hashlib.pbkdf2_hmac(
            'sha256',
            unhashed_password.get_secret_value().encode('utf-8'),
            salt_bytes,
            iterations,
            dklen=32
        )
        
        # Compare the generated hash with the stored hash
        return hmac.compare_digest(binascii.hexlify(new_hashed_password).decode('ascii'), hashed_password)
 
    @staticmethod              
    def create_standard_user(user_registration: UserRegistration, user_collection: Collection) -> str:
        """
        Create a new standard user.
    
        :raises ValueError if one of the expected env variables are not set
        :return: The UUID of the user
        """
        
        salt, hashed_password = UserUtils.hash_password(user_registration.password)
        user_id = str(uuid.uuid4())
        user_object = {
            "user_id": user_id,
            "username": user_registration.username,
            "email": user_registration.email,
            "password": hashed_password,
            "salt": salt,
        }
        
        user_collection.insert_one(user_object)
        return user_id
        
    @staticmethod
    def create_google_user(user_info: Dict[Any, Any], user_collection: Collection) -> str:
        """
        Create a new google user. This user can only be logged in by Google.
    
        :raises ValueError if one of the expected env variables are not set
        :return: The UUID of the user
        """
        
        user_id = str(uuid.uuid4())
        user_object = {
            "user_id": user_id,
            "username": user_info["email"],
            "email": user_info["email"],
            "google_id": user_info["id"]
        }
        
        user_collection.insert_one(user_object)
        return user_id
 
    @staticmethod          
    def get_user_from_email(email: str, user_collection: Collection) -> Dict[Any, Any] | None:
        """
        Get user from a given email. If the user does not exist, None is return.
    
        :param email: The email of a possible user
        :type email: str
        :param user_collection: A Collection of users
        :type user_collection: pymongo.collection.Collection
        :return: The object representing the user
        :rtype: Dict[Any, Any] | None
        """
        
        return user_collection.find_one({"email": email})
        
    @staticmethod          
    def get_user_from_user_id(user_id: str, user_collection: Collection) -> Dict[Any, Any] | None:
        """
        Get user from a given user id. If the user does not exist, None is return.
    
        :param user_id: The user id of a possible user
        :type user_id: str
        :param user_collection: A Collection of users
        :type user_collection: pymongo.collection.Collection
        :return: The object representing the user
        :rtype: Dict[Any, Any] | None
        """
        
        return user_collection.find_one({"user_id": user_id})
     
    @staticmethod      
    def is_email_taken(email: str, user_collection: Collection) -> bool:
        """
        Check if the email belongs to a user.
    
        :param email: The email of a possible user
        :type email: str
        :param user_collection: A Collection of users
        :type user_collection: pymongo.collection.Collection
        :return: True if the email is used by a user.
        :rtype: bool
        """
        
        if user_collection.find_one({"email": email}):
            return True
        else:
            return False

    @staticmethod               
    def is_username_taken(username: str, user_collection: Collection) -> bool:
        """
        Check if the username belongs to a user.
    
        :param username: The username of a possible user
        :type username: str
        :param user_collection: A Collection of users
        :type user_collection: pymongo.collection.Collection
        :return: True if the username is used by a user.
        :rtype: bool
        """
        
        if user_collection.find_one({"username": username}):
            return True
        else:
            return False
            
    @staticmethod
    def get_user_from_google_id(google_id: str, user_collection: Collection) -> Dict[Any, Any] | None:
        """
        Get user from a given google id. If the user does not exist, None is return.
    
        :param google_id: The google id of a possible user
        :type google_id: str
        :param user_collection: A Collection of users
        :type user_collection: pymongo.collection.Collection
        :return: The object representing the user
        :rtype: Dict[Any, Any] | None
        """    
     
        return user_collection.find_one({"google_id": google_id})