
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
        Gets categories from a given category collection table
        
        :param category_collection: The collection of posts to be queried
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
    def is_category(category_collection: Collection, category_id: str) -> bool:
        """
        Checks if a category id belongs to a category
        
        :param category_collection: The collection of posts to be queried
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