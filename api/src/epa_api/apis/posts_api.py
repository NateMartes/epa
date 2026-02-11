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
from typing import Any, Optional
from typing_extensions import Annotated
from epa_api.models.create_post import CreatePost
from epa_api.models.post import Post
from epa_api.models.post_list import PostList
from epa_api.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = epa_api.api_implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/post",
    responses={
        200: {"model": PostList, "description": "A list of posts."},
    },
    tags=["Posts"],
    summary="Retrieve posts",
    response_model_by_alias=True,
)
async def get_posts(
    page_num: Annotated[Optional[StrictStr], Field(description="Start at a specfic page number (if not given, this is always 1)")] = Query(None, description="Start at a specfic page number (if not given, this is always 1)", alias="page_num"),
    post_id: Annotated[Optional[StrictStr], Field(description="Filter by a specific post ID.")] = Query(None, description="Filter by a specific post ID.", alias="post_id"),
    name: Annotated[Optional[StrictStr], Field(description="Filter by post title (case-insensitive search).")] = Query(None, description="Filter by post title (case-insensitive search).", alias="name"),
    category_slug: Annotated[Optional[StrictStr], Field(description="Filter by the URL-friendly category identifier (e.g., 'road-hazard').")] = Query(None, description="Filter by the URL-friendly category identifier (e.g., &#39;road-hazard&#39;).", alias="category_slug"),
    since: Annotated[Optional[datetime], Field(description="Return posts created after this ISO 8601 timestamp.")] = Query(None, description="Return posts created after this ISO 8601 timestamp.", alias="since"),
    user_id: Annotated[Optional[StrictStr], Field(description="Return posts created by a specific user.")] = Query(None, description="Return posts created by a specific user.", alias="user_id"),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> PostList:
    """Returns a list of posts. Supports filtering by ID, name, category, or time.  Results are limited to a maximum of 10. """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().get_posts(page_num, post_id, name, category_slug, since, user_id)


@router.post(
    "/v1/post",
    responses={
        200: {"model": Post, "description": "Successful creation of a post."},
    },
    tags=["Posts"],
    summary="Create a post",
    response_model_by_alias=True,
)
async def create_post(
    create_post: CreatePost = Body(None, description=""),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Post:
    """Creates a post, returning the new post object"""
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().create_post(create_post)


@router.delete(
    "/v1/post",
    responses={
        200: {"description": "Successful deletetion of a post."},
    },
    tags=["Posts"],
    summary="Delete a post",
    response_model_by_alias=True,
)
async def delete_post(
    post_id: Annotated[StrictStr, Field(description="The ID of the post")] = Query(None, description="The ID of the post", alias="post_id"),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> None:
    """Deletes a post"""
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().delete_post(post_id)
