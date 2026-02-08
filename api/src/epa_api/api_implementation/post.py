from epa_api.apis.posts_api_base import BasePostsApi
from typing import Optional
from pydantic import StrictStr
from epa_api.models.post import Post
from epa_api.models.post_list import PostList
from datetime import datetime
from epa_api.api_implementation.utils.mongo import MongoUtils
from epa_api.api_implementation.utils.post import PostUtils

class PostAPIImplementation(BasePostsApi):
    async def get_posts(
        self,
        page_num: Optional[StrictStr],
        post_id: Optional[StrictStr],
        name: Optional[StrictStr],
        category_slug: Optional[StrictStr],
        since: Optional[datetime],
    ) -> PostList:
        
        page_num_int = PostUtils.get_page_num_from_string(page_num)
        page_size = PostUtils.get_page_size()
        client, db = MongoUtils.get_mongodb_database_connection()
        post_collection = MongoUtils.get_post_collection(db)
        results = PostUtils.get_posts(post_collection, page_num=page_num_int, page_size=page_size)
        
        output = PostList(page_number=page_num_int, page_size=page_size, posts=[])
        for post in results:
            if output.posts:
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
                
        client.close()
        return output
        