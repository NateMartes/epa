from epa_api.apis.posts_api_base import BasePostsApi
from typing import Optional
from pydantic import StrictStr
from epa_api.models.post import Post
from epa_api.models.create_post import CreatePost
from epa_api.models.post_list import PostList
from datetime import datetime
from epa_api.api_implementation.utils.mongo import MongoUtils
from epa_api.api_implementation.utils.post import PostUtils
from epa_api.api_implementation.utils.cache import CacheUtils
from epa_api.api_implementation.utils.redis import RedisUtils
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
        is_subscribed: Optional[StrictStr],
    ) -> PostList:
        """Returns a list of posts. Supports filtering by ID, name, category, or time.  Results are limited to a maximum of 10. """

        token = TokenUtils.validate_access_token_with_db()
        requesting_user_id = TokenUtils.get_user_id(token)
        page_num_int = PostUtils.get_page_num_from_string(page_num)
        page_size = PostUtils.get_page_size()
        
        output = None
        
        is_cached_post_request = all([
            is_subscribed == "true",
            page_num_int == 0,
            not any([post_id, name, category_slug, since, user_id])
        ])
        
        if is_cached_post_request:
            
            try:
                # Get user's posts from cache
                rdb = RedisUtils.get_redis_connection()
                posts = await CacheUtils.get_user_subscribed_posts(rdb, requesting_user_id)
                if posts:
                    output = PostUtils.get_post_list(posts, page_num_int, len(posts))
                    
                # Clear cache if it exists
                if output:
                    try:
                        await CacheUtils.clear_user_subscribed_posts(rdb, requesting_user_id)
                    except Exception as e:
                        logging.getLogger(__name__).warning(f"Failed to clear cached post request: {e}")
                        
                # Disconnect
                await RedisUtils.close(rdb)
                    
            except Exception as e:
                logging.getLogger(__name__).warning(f"an error occured while using cache: {e}, Defaulting to database")
                
        if output and output.posts:
            cahced_posts_length = len(output.posts)
            if cahced_posts_length == page_size:
                return output
            elif cahced_posts_length > page_size:
                output.posts[:page_size]
                return output
            else:
                # Keep the posts we got from cache and get the rests of the posts from the db
                page_size -= cahced_posts_length
                        
        query = PostUtils.build_post_query(
            post_id=post_id, name=name, 
            category_slug=category_slug, 
            since=since, 
            user_id=user_id
        )
        
        client, db = MongoUtils.get_mongodb_database_connection()
        post_collection = MongoUtils.get_post_collection(db)
        if is_subscribed:
            
            subscribed_categories = CategoryUtils.get_all_user_subscribed_categories(
                user_id=requesting_user_id,
                user_collection=MongoUtils.get_user_collection(db),
                category_collection=MongoUtils.get_categories_collection(db)
            )
            
            PostUtils.add_is_subscribed_field_to_post_query(
                post_query=query,
                is_subscribed=is_subscribed,
                subscribed_categories=subscribed_categories
            )
            
        # Don't get cached posts during db query
        if output and output.posts:
            PostUtils.add_post_exclusions_to_post_query(query, output)
                    
        results = PostUtils.get_posts(post_collection, query=query, page_num=page_num_int, page_size=page_size)
        results = list(results)
        
        # If the cached output exists, extend the cache results with the ones from the database
        if output and output.posts and output.page_size:
            rest_of_page = PostUtils.get_post_list(results, page_num_int, len(results))
            output.posts.extend(rest_of_page.posts if rest_of_page.posts else [])
            output.page_size += rest_of_page.page_size if rest_of_page.page_size else 0
        else:
            output = PostUtils.get_post_list(results, page_num_int, len(results))
                
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
            
        