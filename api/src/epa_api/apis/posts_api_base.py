# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from datetime import datetime
from pydantic import Field, StrictStr
from typing import List, Optional
from typing_extensions import Annotated
from epa_api.models.post import Post


class BasePostsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePostsApi.subclasses = BasePostsApi.subclasses + (cls,)
    async def get_posts(
        self,
        post_id: Annotated[Optional[StrictStr], Field(description="Filter by a specific post ID.")],
        name: Annotated[Optional[StrictStr], Field(description="Filter by post title (case-insensitive search).")],
        category_slug: Annotated[Optional[StrictStr], Field(description="Filter by the URL-friendly category identifier (e.g., 'road-hazard').")],
        since: Annotated[Optional[datetime], Field(description="Return posts created after this ISO 8601 timestamp.")],
    ) -> List[Post]:
        """Returns a list of posts. Supports filtering by ID, name, category, or time.  Results are limited to a maximum of 10. """
        ...
