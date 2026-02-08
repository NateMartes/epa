from fastapi.exceptions import HTTPException
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from fastapi import status
from pydantic import StrictStr
from typing import Dict, Any
import logging
import os

class PostUtils:
    @staticmethod
    def get_page_num_from_string(page_num: StrictStr | None) -> int:
        page_num_int = 0
        if page_num:
            try:
                page_num_int = int(page_num)
                if page_num_int < 0:
                    raise ValueError
            except TypeError or ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid value {page_num}")
                
        return page_num_int
        
    @staticmethod
    def get_page_size() -> int:
        val = os.getenv("EPA_API_PAGE_SIZE")
        if not val:
            logging.getLogger(__name__).debug("Environment variable EPA_API_PAGE_SIZE not set. Defaulting to 10")
            val = 10
        else:
            try:
                val = int(val)
            except TypeError:
                logging.getLogger(__name__).debug("Environment variable EPA_API_PAGE_SIZE not an int. Defaulting to 10")
                val = 10

        return val
        
    @staticmethod
    def get_posts(post_collection: Collection, query: Dict[Any, Any] = {}, page_num: int = 0, page_size: int = 10) -> Cursor:
        return post_collection.find(query).skip(page_size * page_num).limit(page_size)
