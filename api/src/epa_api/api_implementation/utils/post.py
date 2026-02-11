from fastapi.exceptions import HTTPException
from fastapi import status
from starlette.types import HTTPExceptionHandler
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
import re

class PostUtils
    """A class with helpful methods to interact with a posts in the database"""

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
        Get the page size define for posts. This uses the environment variable EPA_API_PAGE_SIZE,
        which if not set, defaults to some int.
        
        :return: The page size
        :rtype: int
        """
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
    def build_post_query(post_id: StrictStr | None = None,
        name: StrictStr | None = None,
        category_slug: StrictStr | None = None,
        since: datetime | None = None,
        user_id: StrictStr | None = None
    ) -> Dict[Any, Any]:
        """
        Builds a query for interacting with the post collection.
        
        :param post_id: The id of a post
        :type post_id: StrictStr | None
        :param name: The title of a post
        :type name: StrictStr | None
        :param category_slug: The category of a post
        :type category_slug: StrictStr | None
        :param since: All posts since a specfic date
        :type since: datetime | None
        :param user_id: The user who created posts
        :type user_id: StrictStr | None
        :return: A valid query to use aganist a post collection
        :rtype: Dict[Any, Any]
        """
        output = {}
        
        if post_id:
            output["post_id"] = post_id
        if name:
            output["title"] = {"$regex": re.escape(name), "$options": "i"}
        if category_slug:
            output["category_slug"] = category_slug
        if since:
            output["created_at"] = {"$gte": since.isoformat()}
        if user_id:
            output["created_by"] = user_id
            
        return output
        
    @staticmethod
    def get_posts(post_collection: Collection, query: Dict[Any, Any] = {}, page_num: int = 0, page_size: int = 10) -> Cursor:
        """
        Gets posts from a given post collection table
        
        :param post_collection: The collection of posts to be queried
        :type post_collection: pymongo.Collection
        :param query: The query to use
        :type query: Dict[Any, Any]
        :param page_num: The page num to return, defaults to the head (0)
        :type page_num: int
        :param page_size: The size of the page, defaults to 10
        :type page_size: int
        :return: A cursor with the results
        :rtype: pymongo.Cursor
        """
        return post_collection.find(query).skip(page_size * page_num).limit(page_size)
        
    @staticmethod
    def validate_post(create_post_object: CreatePost) -> bool:
        """
        Validates if a post object is semeantically correct.
        :param create_post_object: The object representing a new post to create
        :type create_post_object: CreatePost
        :return: True if and only if the post in valid
        :rtype: bool
        """
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
        """
        Creates a post in the post collection.
        
        :param post_collection: The collection of posts to be queried
        :type post_collection: pymongo.Collection
        :param user_id: The id to makes this post on behalf of
        :type user_id: str
        :param category_slug: The category this post belongs to
        :type category_slug: str
        :param create_post_object: The new post to create
        :type create_post_object: CreatePost
        :return: The new created post
        :rtype: Post
        """
        
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
        
    @staticmethod
    def delete_post(post_collection: Collection, post_id: str, user_id: str):
        """
        Deletes a post in the post collection. This will fail if the user id given does not match the what is on th post id.
        
        :param post_collection: The collection of posts
        :type post_collection: pymongo.Collection
        :param post_id: The id of the post to delete
        :type post_id: str
        :param user_id: The id of who owns the post
        :type user_id: str
        """
        
        query = PostUtils.build_post_query(post_id=post_id)
        val = post_collection.count_documents(query)
        if val != 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        
        res = PostUtils.get_posts(post_collection, query)
        post = res.next()
        
        if post["created_by"] != user_id:
            res.close()
            raise HTTPException(status_code=status.HTTP_401_NOT_FOUND, detail=f"This post does not belong to {user_id}")
        
        res.close()
        post_collection.delete_one(query)

