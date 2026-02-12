# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from epa_api.apis.category_api_base import BaseCategoryApi
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
from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from epa_api.models.category_list import CategoryList
from epa_api.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = epa_api.api_implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/category",
    responses={
        200: {"model": CategoryList, "description": "Successful creation of a post."},
    },
    tags=["Category"],
    summary="Gets a list of categories",
    response_model_by_alias=True,
)
async def get_categories(
    page_num: Annotated[Optional[StrictStr], Field(description="Start at a specfic page number (if not given, this is always 0)")] = Query(None, description="Start at a specfic page number (if not given, this is always 0)", alias="page_num"),
    category_id: Annotated[Optional[StrictStr], Field(description="Search for a specific category ID")] = Query(None, description="Search for a specific category ID", alias="category_id"),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> CategoryList:
    """Gets a list of categories"""
    if not BaseCategoryApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCategoryApi.subclasses[0]().get_categories(page_num, category_id)
