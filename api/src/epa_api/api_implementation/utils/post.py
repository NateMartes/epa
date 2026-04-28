from epa_api.api_implementation.utils.kafka import KafkaUtils
from epa_api.api_implementation.utils.category import CategoryUtils
from fastapi.exceptions import HTTPException
from fastapi import status
from epa_api.models.post import Post
from epa_api.models.post_list import PostList
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

class PostUtils:
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
        Get the page size define for posts. This uses the environment variable EPA_API_POST_PAGE_SIZE,
        which if not set, defaults to some int.
        
        :return: The page size
        :rtype: int
        """
        val = os.getenv("EPA_API_POST_PAGE_SIZE")
        if not val:
            logging.getLogger(__name__).debug("Environment variable EPA_API_POST_PAGE_SIZE not set. Defaulting to 10")
            val = 10
        else:
            try:
                val = int(val)
            except TypeError:
                logging.getLogger(__name__).debug("Environment variable EPA_API_POST_PAGE_SIZE not an int. Defaulting to 10")
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
    def add_is_subscribed_field_to_post_query(
        post_query: Dict[Any, Any],
        is_subscribed: StrictStr,
        subscribed_categories: Cursor | None
    ):
        """
        Given a category_query, add the is_subscribed query parameter to it.
        
        :param post_query: A query generated from PostUtils.build_post_query()
        :type post_query: Dict[Any, Any]
        :param is_subscribed: true if the post that would be return, the user would be subscribed to
        :type is_subscribed: str
        :param subscribed_categories: A cursor containing the categories a user is subscribed to
        :type subscribed_categories: Cursor | None
        """
            
        if not subscribed_categories:
            # Don't match any categories since the user is subscribed to no categories
            post_query["category_slug"] = {"$in": []}
        else:
            category_list = list(subscribed_categories)
            subscribed_ids = [cat["category_id"] for cat in category_list]
            
            # Handled for category_id already existing in the category_query
            val = post_query.get("category_slug", None)
            if val:
                if val not in subscribed_ids:
                    # The user is not subscribed to this category, so don't match any categories
                    # This would be very bad way to check if a user was subscribed to a category
                    post_query["category_slug"] = {"$in": []}
            else:
                # Ensure that all posts must reside in the user's subscribed_categories
                post_query["category_slug"] = {"$in": subscribed_ids}   
       
        if is_subscribed == "false":
            post_query["category_slug"] = {"$not": post_query["category_slug"]}
            
    @staticmethod
    def add_post_exclusions_to_post_query(post_query: Dict[Any, Any], post_exclusion_list: PostList):
        """
        Given a list of posts, ensure that when this query is executed, the posts
        in this list do not appear in the query list.
        
        :param post_query: A post query to alter
        :type post_query: Dict[Any, Any]
        :param post_exclusion_list: A list of posts to exclude
        :type post_exclusion_list: PostList
        """
        
        if not post_exclusion_list.posts:
            return
            
        post_ids = [p.post_id for p in post_exclusion_list.posts]
        if "post_id" not in post_query:
                post_query["post_id"] = {}
        elif not isinstance(post_query["post_id"], Dict):
            return
            
        post_query["post_id"]["$nin"] = post_ids
                        
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
        
        # A database index should be set to have the created_at fied be descending
        return post_collection.find(query).sort("created_at", -1).skip(page_size * page_num).limit(page_size)
        
    @staticmethod
    def validate_post(create_post_object: CreatePost, category_collection: Collection) -> bool:
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
            
        if not CategoryUtils.is_category(category_collection, str(create_post_object.category_slug)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
            
        return True
        
    @staticmethod
    def create_post(post_collection: Collection, user_id: str, username: str, category: str, category_slug: str, create_post_object: CreatePost) -> Post:
        """
        Creates a post in the post collection.
        
        :param post_collection: The collection of posts to be queried
        :type post_collection: pymongo.Collection
        :param user_id: The id to makes this post on behalf of
        :type user_id: str
        :param username: The username of the user to makes this post on behalf of
        :type username: str
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
            "username": username,
            "title": create_post_object.title,
            "content": create_post_object.content,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "category": category,
            "category_slug": category_slug
        }
        
        # Push to kafka queue
        producer = KafkaUtils.connect_to_kafka_as_producer()
        KafkaUtils.send_message(producer, new_post)
        producer.close()
        
        # FOR TESTING, REMOVE IN PRODUCTION
        post_collection.insert_one(new_post)
        
        return Post(
            post_id=new_post["post_id"],
            created_by=new_post["created_by"],
            username=username,
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


    @staticmethod
    def get_post_list(posts: list[Dict[Any, Any]], page_num: int, page_size: int) -> PostList:
        """
        Given a list of raw posts, convert into a PostList object.
        
        :param posts: A list of dictonaries representing raw posts, usually from the database
        :type posts: list[Dict[Any, Any]]
        :param page_num: The page number to set this post list as
        :param page_num: int
        :param page_num: The page size of this page, should match the length of posts
        :type page_num: int
        :return: A new PostLIst object
        """
        
        output = PostList(page_number=page_num, page_size=page_size, posts=[])
        for post in posts:
            if isinstance(output.posts, list):
                try:
                    output.posts.append(
                        Post(
                            post_id=post["post_id"],
                            title=post["title"],
                            content=post["content"],
                            category=post["category"],
                            category_slug=post["category_slug"],
                            created_at=post["created_at"],
                            created_by=post["created_by"],
                            username=post["username"]
                        )
                    )
                except KeyError:
                    logging.getLogger(__name__).warning(f"Failed to get document {post}. Unexpected structure")
                    
        return output