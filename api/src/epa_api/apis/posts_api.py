# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from epa_api.apis.posts_api_base import BasePostsApi
import epa_api.api_implementation

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from epa_api.models.extra_models import TokenModel  # noqa: F401
from datetime import datetime
from pydantic import Field, StrictStr
from typing import List, Optional
from typing_extensions import Annotated
from epa_api.models.post import Post


router = APIRouter()

ns_pkg = epa_api.api_implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/post",
    responses={
        200: {"model": List[Post], "description": "A list of posts."},
    },
    tags=["Posts"],
    summary="Retrieve posts",
    response_model_by_alias=True,
)
async def get_posts(
    post_id: Annotated[Optional[StrictStr], Field(description="Filter by a specific post ID.")] = Query(None, description="Filter by a specific post ID.", alias="post_id"),
    name: Annotated[Optional[StrictStr], Field(description="Filter by post title (case-insensitive search).")] = Query(None, description="Filter by post title (case-insensitive search).", alias="name"),
    category_slug: Annotated[Optional[StrictStr], Field(description="Filter by the URL-friendly category identifier (e.g., 'road-hazard').")] = Query(None, description="Filter by the URL-friendly category identifier (e.g., &#39;road-hazard&#39;).", alias="category_slug"),
    since: Annotated[Optional[datetime], Field(description="Return posts created after this ISO 8601 timestamp.")] = Query(None, description="Return posts created after this ISO 8601 timestamp.", alias="since"),
) -> List[Post]:
    """Returns a list of posts. Supports filtering by ID, name, category, or time.  Results are limited to a maximum of 10. """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().get_posts(post_id, name, category_slug, since)
