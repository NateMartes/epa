from fastapi.exceptions import HTTPException
from fastapi import status
from epa_api.models.post import Post
from epa_api.models.create_post import CreatePost
from datetime import datetime
from datetime import timezone
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pydantic import StrictStr
from typing import Dict, Any
import logging
import os
import uuid

class PostUtils:
    @staticmethod
    def get_page_num_from_string(page_num: StrictStr | None) -> int:
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
        
    @staticmethod
    def validate_post(create_post_object: CreatePost) -> bool:
        if not create_post_object or not create_post_object.model_validate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if create_post_object.title == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")
        if create_post_object.content == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content cannot be empty")
            
        # Add later if create_post_object.category_slug
        return True
        
    @staticmethod
    def create_post(post_collection: Collection, user_id: str, category: str, category_slug: str, create_post_object: CreatePost) -> Post:
        new_post = {
            "post_id": str(uuid.uuid4()),
            "created_by": user_id,
            "title": create_post_object.title,
            "content": create_post_object.content,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "category": category,
            "category_slug": category_slug
        }
        
        # Push to kafka queue
        post_collection.insert_one(new_post)
        
        return Post(
            post_id=new_post["post_id"],
            created_by=new_post["created_by"],
            title=new_post["title"],
            content=new_post["content"],
            created_at=new_post["created_at"],
            category=new_post["category"],
            category_slug=new_post["category_slug"]
        )

