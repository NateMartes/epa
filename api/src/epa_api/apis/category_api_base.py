# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from epa_api.models.category_list import CategoryList
from epa_api.models.subscribe_category_request import SubscribeCategoryRequest
from epa_api.security_api import get_token_BearerAuth

class BaseCategoryApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCategoryApi.subclasses = BaseCategoryApi.subclasses + (cls,)
    async def get_categories(
        self,
        page_num: Annotated[Optional[StrictStr], Field(description="Start at a specfic page number (if not given, this is always 0)")],
        category_id: Annotated[Optional[StrictStr], Field(description="Search for a specific category ID")],
    ) -> CategoryList:
        """Gets a list of categories"""
        ...


    async def get_user_subscribed_categories(
        self,
        page_num: Annotated[Optional[StrictStr], Field(description="Start at a specfic page number (if not given, this is always 0)")],
    ) -> CategoryList:
        """Get users subscribed categories"""
        ...


    async def subscribe_to_category(
        self,
        subscribe_category_request: SubscribeCategoryRequest,
    ) -> None:
        """Subscribe a user to a category"""
        ...


    async def unsubcribed_user_from_category(
        self,
        subscribe_category_request: SubscribeCategoryRequest,
    ) -> None:
        """Unsubscribe a user from a category"""
        ...
