from typing import List, Tuple
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
import logging

class MongoUtils:
    """A class with helpful methods to interact with MongoDB"""
    
    @staticmethod
    def get_mongodb_env_variables() -> Tuple[str, int, str, str, List[str]]:
        """
        Get MongoDB env variables.
    
        :raises ValueError if one of the expected env variables are not set
        :return: A tupe containing the values of the env variables as such:
            - Hostname
            - Port
            - Username
            - Password
            - A list of collections
        :rtype: Tuple[str, int, str, str, List[str]]
        """
        
        output = []
        collection_output = []
        
        env_vars = [
            "EPA_MONGODB_HOSTNAME",
            "EPA_MONGODB_PORT",
            "EPA_MONGODB_USERNAME",
            "EPA_MONGODB_PASSWORD",
        ]
        
        env_collection_vars = [
            "EPA_MONGODB_USER_COLLECTION",
            "EPA_MONGODB_SESSION_TOKEN_COLLECTION",
            "EPA_MONGODB_POSTS_COLLECTION",
            "EPA_MONGODB_CATEGORIES_COLLECTION"
        ]
        
        for var in env_vars:
            val = os.getenv(var)
            if not val:
                raise ValueError(f"Expected environment variable {var} not set")
            output.append(val)
    
        for var in env_collection_vars:
            val = os.getenv(var)
            if not val:
                raise ValueError(f"Expected environment variable {var} not set") 
            collection_output.append(val)
            
        output.append(collection_output)
        return tuple(output)
        
    @staticmethod        
    def get_mongodb_database_connection() -> Tuple[MongoClient, Database]:
        """
        Get MongoDB database connection.
    
        :raises ValueError if one of the expected env variables are not set.
        :return: A connection to a MongoDB database
        :rtype: Tuple[pymongo.MongoClient, pymongo.database.Database]
        """
        
        is_cluster = 1
        try:
            tmp = os.getenv("EPA_MONGODB_IS_CLUSTER")
            if not tmp:
                logging.getLogger(__name__).warning("Environment variable EPA_MONGODB_IS_CLUSTER not given, assuming MongoDB is a cluster")
            else:
               if int(tmp) == 0:
                   is_cluster = 0
                
        except TypeError:
            logging.getLogger(__name__).warning("Environment variable EPA_MONGODB_IS_CLUSTER not right type, assuming MongoDB is a cluster")
            
        hostname, port, username, password, _ = MongoUtils.get_mongodb_env_variables()
        if is_cluster:
            uri = f"mongodb+srv://{username}:{password}@{hostname}/"
        else:
            uri = f"mongodb://{username}:{password}@{hostname}:{port}/"
            
        client = MongoClient(uri, timeoutMS=5000)
        try:
            db = client["epa_database"]
            return client, db
        except Exception:
            raise ValueError("Expected database epa_database does not exist")
    
    @staticmethod               
    def get_user_collection(db: Database) -> Collection:
        """
        Get the user collection in the MongoDB database.
    
        :param db: The MongoDB Database
        :type db: pymongo.database.Database
        :return: A collection from the MongoDB database
        :rtype: pymongo.collection.Collection
        """
        
        collections_index = -1
        user_collection_index = 0
        user_collection_name =  MongoUtils.get_mongodb_env_variables()[collections_index][user_collection_index]
        return db[user_collection_name]
 
    @staticmethod       
    def get_session_tokens_collection(db: Database) -> Collection:
        """
        Get the session token collection in the MongoDB database.
        
        :param db: The MongoDB Database
        :type db: pymongo.database.Database
        :return: A collection from the MongoDB database
        :rtype: pymongo.collection.Collection
        """
        
        collections_index = -1
        session_token_collection_index = 1
        session_token_collection_name =  MongoUtils.get_mongodb_env_variables()[collections_index][session_token_collection_index]
        return db[session_token_collection_name]
  
    @staticmethod       
    def get_post_collection(db: Database) -> Collection:
        """
        Get the post collection in the MongoDB database.
        
        :param db: The MongoDB Database
        :type db: pymongo.database.Database
        :return: A collection from the MongoDB database
        :rtype: pymongo.collection.Collection
        """
        
        collections_index = -1
        post_collection_index = 2
        post_collection_index_name =  MongoUtils.get_mongodb_env_variables()[collections_index][post_collection_index]
        return db[post_collection_index_name]
        
    @staticmethod       
    def get_categories_collection(db: Database) -> Collection:
        """
        Get the categories collection in the MongoDB database.
        
        :param db: The MongoDB Database
        :type db: pymongo.database.Database
        :return: A collection from the MongoDB database
        :rtype: pymongo.collection.Collection
        """
        
        collections_index = -1
        categories_collection_index = 3
        post_collection_index_name =  MongoUtils.get_mongodb_env_variables()[collections_index][categories_collection_index]
        return db[post_collection_index_name]      
        

    
    