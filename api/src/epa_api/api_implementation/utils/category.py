from epa_api.models.subscribe_category_request import SubscribeCategoryRequest
from epa_api.models.category_list import CategoryList
from epa_api.api_implementation.utils.user import UserUtils
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Dict, Any
from pydantic import StrictStr
from pymongo.collection import Collection
from pymongo.cursor import Cursor
import os
import logging

class CategoryUtils:
    """A class with helpful methods to interact with categories in the database"""
    
    @staticmethod
    def get_page_num_from_string(page_num: StrictStr | None) -> int:
        """
        Given a page number as a string, convert it into a int.
        
        :param page_num: The possbile page number as a string
        :type page_num: StrictStr | None
        :return: An integer representation of the number
        :rtype: int
        :raises: HTTPException if the value of the page number is invalid, meaning it exists but it is an invalid integer
        """
        page_num_int = 0
        if page_num:
            try:
                page_num_int = int(page_num)
                if page_num_int < 0:
                    raise TypeError
            except TypeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid value {page_num}")
                
        return page_num_int
        
    @staticmethod
    def get_page_size() -> int:
        """
        Get the page size define for posts. This uses the environment variable EPA_API_CATEGORY_PAGE_SIZE,
        which if not set, defaults to some int.
        
        :return: The page size
        :rtype: int
        """
        val = os.getenv("EPA_API_CATEGORY_PAGE_SIZE")
        if not val:
            logging.getLogger(__name__).debug("Environment variable EPA_API_CATEGORY_PAGE_SIZE not set. Defaulting to 10")
            val = 10
        else:
            try:
                val = int(val)
            except TypeError:
                logging.getLogger(__name__).debug("Environment variable EPA_API_CATEGORY_PAGE_SIZE not an int. Defaulting to 10")
                val = 10

        return val
        
    @staticmethod
    def build_category_query(category_id: StrictStr | None = None,
    ) -> Dict[Any, Any]:
        """
        Builds a query for interacting with the post collection.
        
        :param category_id: The id of a category
        :type category_id: StrictStr | None
        :return: A valid query to use aganist a post collection
        :rtype: Dict[Any, Any]
        """
        output = {}
        
        if category_id:
            output["category_id"] = category_id
            
        return output
            
    @staticmethod
    def get_categories(category_collection: Collection, query: Dict[Any, Any] = {}, page_num: int = 0, page_size: int = 10) -> Cursor:
        """
        Gets categories from a given category collection table.
        
        :param category_collection: The collection of categories to query
        :type category_collection: pymongo.Collection
        :param page_num: The page num to return, defaults to the head (0)
        :type page_num: int
        :param page_size: The size of the page, defaults to 10
        :type page_size: int
        :return: A cursor with the results
        :rtype: pymongo.Cursor
        """
        return category_collection.find(query).skip(page_size * page_num).limit(page_size)
        
    @staticmethod
    def get_user_subscribed_categories(user_id: str, user_collection: Collection, category_collection: Collection, page_num: int = 0, page_size: int = 10) -> Cursor | None:
        """
        Gets categories for a specfic user.
        
        :param category_collection: The collection of categories to query
        :type category_collection: pymongo.Collection
        :param user_collection: The collection of users to query
        :type user_collection: pymongo.Collection
        :param page_num: The page num to return, defaults to the head (0)
        :type page_num: int
        :param page_size: The size of the page, defaults to 10
        :type page_size: int
        :return: A cursor with the results, None if there are no categories the user has subscribed to
        :rtype: pymongo.Cursor | None
        """
        
        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        if not user:
            return None
            
        subscribed_categories = user.get("subscribed", None)
        if not subscribed_categories:
            return None
            
        # Build query to get user categories from categories collection
        query = {"category_id": {"$in": subscribed_categories}}
            
        return category_collection.find(query).skip(page_size * page_num).limit(page_size)
        
    @staticmethod
    def get_all_user_subscribed_categories(user_id: str, user_collection: Collection, category_collection: Collection) -> Cursor | None:
        """
        Gets all categories for a specfic user.
        
        :param category_collection: The collection of categories to query
        :type category_collection: pymongo.Collection
        :param user_collection: The collection of users to query
        :type user_collection: pymongo.Collection
        :return: A cursor with the results, None if there are no categories the user has subscribed to
        :rtype: pymongo.Cursor | None
        """
        
        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        if not user:
            return None
            
        subscribed_categories = user.get("subscribed", None)
        if not subscribed_categories:
            return None
            
        # Build query to get user categories from categories collection
        query = {"category_id": {"$in": subscribed_categories}}
            
        return category_collection.find(query)
        
    @staticmethod
    def get_category_list(categories: list, page_num: int, page_size: int) -> CategoryList:
        """
        Get a CategoryList object from a list of raw categories.
        
        :param categories: A list of raw categories, in the format [{"category_id": ..., "category_name": ...}]
        :type categories: list
        :param page_num: The page number to set this category list as
        :param page_num: int
        :param page_num: The page size of this page, should match the length of categories
        :type page_num: int
        :return: The new CategoryList
        :rtype: CategoryList
        """
        output = CategoryList(page_number=page_num, page_size=page_size, categories=[])
        for category in categories:
            if isinstance(output.categories, list):
                try:
                    output.categories.append(
                        {
                            "category_id": category["category_id"],
                            "category_name": category["category_name"]
                        }
                    )
                except KeyError:
                    logging.getLogger(__name__).warning(f"Failed to get document {category}. Unexpected structure")
                    
        return output
        
    @staticmethod
    def is_category(category_collection: Collection, category_id: str) -> bool:
        """
        Checks if a category id belongs to a category.
        
        :param category_collection: The collection of categories to check
        :type category_collection: pymongo.Collection
        :param category_id: The id of a possbile category
        :type category_id: str
        :return: True and only if the category exists
        :rtype: bool
        """
        res = category_collection.find_one(CategoryUtils.build_category_query(category_id=category_id))
        if not res:
            return False
        return True
        
    @staticmethod
    def is_user_subscribed_to_category(user_collection: Collection, user_id: str, category_id: str) -> bool:
        """
        Checks if a category id is in the user's subscribed categories.
        
        :param user_collection: The collection of users to check
        :type user_collection: pymongo.Collection
        :param category_id: The id of a possbile category
        :type category_id: str
        :return: True and only if the category is subscribed to by the user
        :rtype: bool
        """
        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        if not user:
            raise KeyError("User does not exsit")
            
        subscribed_categories = user.get("subscribed", None)
        if not subscribed_categories:
            return False
            
        for category in subscribed_categories:
            if category == category_id:
                return True
                
        return False
        
    @staticmethod
    def validate_subscribe_category_request(request: SubscribeCategoryRequest | None, user_id: str, category_collection: Collection, user_collection: Collection) -> bool:
        """
        Checks if the subscribe request is a valid request.
        
        :param request: The subscribe category request
        :type request: SubscribeCategoryRequest
        :param user_id: The id of the user who made the request
        :type user_id: str
        :param category_collection: The collection of posts to be queried
        :type category_collection: pymongo.Collection
        :param category_collection: The collection of posts to be queried
        :type category_collection: pymongo.Collection
        :param user_collection: The collection of users to check if the category is already subscribed to
        :type user_collection: pymongo.Collection
        :return: True and only if the request is valid
        :rtype: bool
        """
        
        if not request or not request.model_validate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
        if request.category_id == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id cannot be empty")
            
        # Make sure category exists
        if not CategoryUtils.is_category(category_collection, request.category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Make sure user is not already subscribed
        if CategoryUtils.is_user_subscribed_to_category(user_collection, user_id, request.category_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already subscribed")

        return True

    @staticmethod
    def validate_unsubscribe_category_request(request: SubscribeCategoryRequest | None, user_id: str, category_collection: Collection, user_collection: Collection) -> bool:
        """
        Checks if the unsubscribe subscribe request is a valid request.
        
        :param request: The subscribe category request
        :type request: SubscribeCategoryRequest
        :param user_id: The id of the user who made the request
        :type user_id: str
        :param category_collection: The collection of posts to be queried
        :type category_collection: pymongo.Collection
        :param category_collection: The collection of posts to be queried
        :type category_collection: pymongo.Collection
        :param user_collection: The collection of users to check if the category is already subscribed to
        :type user_collection: pymongo.Collection
        :return: True and only if the request is valid
        :rtype: bool
        """
        
        if not request or not request.model_validate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
        if request.category_id == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id cannot be empty")
            
        # Make sure category exists
        if not CategoryUtils.is_category(category_collection, request.category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Make sure user is already subscribed
        if not CategoryUtils.is_user_subscribed_to_category(user_collection, user_id, request.category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not subscribed")

        return True
        
    @staticmethod 
    def subscribe_user_to_category(user_id: str, user_collection: Collection, category_id: str):
        """
        Adds a category to a user's subscribed category list.
        This should only be called after using CategoryUtils.validate_subscribe_category_request
        
        :param user_id: The id of the user who made the request
        :type user_id: str
        :param user_collection: The collection of users to check if the category is already subscribed to
        :type user_collection: pymongo.Collection
        :param category_id: The id of a category
        :type category_id: str
        """
        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        if not user:
            raise KeyError("User does not exsit")
            
        # Assume the user has not subscribed categories
        query = {"user_id": user["user_id"]}
        update_operation = {"$set": {"subscribed": [category_id]}}
        
        subscribed_categories = user.get("subscribed", None)
        if not subscribed_categories:
            user_collection.update_one(query, update_operation)
        else:
            # This should be a list, check anyway
            if isinstance(subscribed_categories, list):
                subscribed_categories.append(category_id)
                update_operation = {"$set": {"subscribed": subscribed_categories}}
                user_collection.update_one(query, update_operation)
            else:
                raise TypeError(f"Expected subscribed_categories to be list, but got {type(subscribed_categories)}")
                
    @staticmethod 
    def unsubscribe_user_from_category(user_id: str, user_collection: Collection, category_id: str):
        """
        Removes a category from a user's subscribed category list.
        This should only be called after using CategoryUtils.validate_subscribe_category_request
        
        :param user_id: The id of the user who made the request
        :type user_id: str
        :param user_collection: The collection of users to check if the category is already subscribed to
        :type user_collection: pymongo.Collection
        :param category_id: The id of a category
        :type category_id: str
        """
        user = UserUtils.get_user_from_user_id(user_id, user_collection)
        if not user:
            raise KeyError("User does not exsit")
            
        query = {"user_id": user["user_id"]}
        update_operation = {"$set": {"subscribed": []}}
        
        subscribed_categories = user.get("subscribed", None)
        if not subscribed_categories:
            raise ValueError("Subscribed category does not exist")
        else:
            # This should be a list, check anyway
            if isinstance(subscribed_categories, list):
                new_subscribed_categories = []
                for category in subscribed_categories:
                    if category == category_id:
                        continue
                    new_subscribed_categories.append(category)
                update_operation = {"$set": {"subscribed": new_subscribed_categories}}
                user_collection.update_one(query, update_operation)
            else:
                raise TypeError(f"Expected subscribed_categories to be list, but got {type(subscribed_categories)}")

