# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from epa_api.models.category_list import CategoryList
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
