from epa_api.apis.posts_api_base import BasePostsApi
from typing import Optional
from pydantic import StrictStr
from epa_api.models.post import Post
from epa_api.models.create_post import CreatePost
from epa_api.models.post_list import PostList
from datetime import datetime
from epa_api.api_implementation.utils.mongo import MongoUtils
from epa_api.api_implementation.utils.post import PostUtils
from epa_api.api_implementation.utils.token import TokenUtils
from epa_api.api_implementation.utils.category import CategoryUtils
import logging


class PostAPIImplementation(BasePostsApi):
    async def get_posts(
        self,
        page_num: Optional[StrictStr],
        post_id: Optional[StrictStr],
        name: Optional[StrictStr],
        category_slug: Optional[StrictStr],
        since: Optional[datetime],
        user_id: Optional[StrictStr],
    ) -> PostList:
        """Returns a list of posts. Supports filtering by ID, name, category, or time.  Results are limited to a maximum of 10. """

        TokenUtils.validate_access_token_with_db()
        
        page_num_int = PostUtils.get_page_num_from_string(page_num)
        page_size = PostUtils.get_page_size()
        
        client, db = MongoUtils.get_mongodb_database_connection()
        post_collection = MongoUtils.get_post_collection(db)
        
        query = PostUtils.build_post_query(post_id=post_id, name=name, category_slug=category_slug, since=since, user_id=user_id)
        results = PostUtils.get_posts(post_collection, query=query, page_num=page_num_int, page_size=page_size)
        results = list(results)
        
        page_size = len(results)
        output = PostList(page_number=page_num_int, page_size=page_size, posts=[])
        for post in results:
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
                            created_by=post["created_by"]
                        )
                    )
                except KeyError:
                    logging.getLogger(__name__).warning(f"Failed to get document {post}. Unexpected structure")
                
        client.close()
        return output
        
    async def create_post(
        self,
        create_post: CreatePost,
    ) -> Post:
        """Creates a post, returning the new post object"""

        token = TokenUtils.validate_access_token_with_db()
        client, db = MongoUtils.get_mongodb_database_connection()
        post_collection = MongoUtils.get_post_collection(db)
        category_collection = MongoUtils.get_categories_collection(db)
        
        PostUtils.validate_post(create_post, category_collection)
        
        output = PostUtils.create_post(post_collection, 
            TokenUtils.get_user_id(token), 
            list(CategoryUtils.get_categories(
                category_collection, 
                query=CategoryUtils.build_category_query(category_id=create_post.category_slug))
            )[0]["category_name"],
            str(create_post.category_slug), 
            create_post
        )
        client.close()
        
        return output
        
    async def delete_post(
        self,
        post_id: StrictStr
    ) -> None:
        """Deletes a post"""

        token = TokenUtils.validate_access_token_with_db()
        
        client, db = MongoUtils.get_mongodb_database_connection()
        post_collection = MongoUtils.get_post_collection(db)

        PostUtils.delete_post(post_collection, post_id, TokenUtils.get_user_id(token))
        
        client.close()
            
        