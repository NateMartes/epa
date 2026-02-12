from epa_api.apis.category_api import BaseCategoryApi
from epa_api.models.category_list import CategoryList
from typing import Optional
from pydantic import StrictStr
from epa_api.api_implementation.utils.token import TokenUtils
from epa_api.api_implementation.utils.category import CategoryUtils
from epa_api.api_implementation.utils.mongo import MongoUtils
import logging

class PostAPIImplementation(BaseCategoryApi):
    async def get_categories(
        self,
        page_num: Optional[StrictStr],
        category_id: Optional[StrictStr]
    ) -> CategoryList:
        """Gets a list of categories"""
        
        TokenUtils.validate_access_token_with_db()
        page_num_int = CategoryUtils.get_page_num_from_string(page_num)
        page_size = CategoryUtils.get_page_size()
        
        client, db = MongoUtils.get_mongodb_database_connection()
        categories_collection = MongoUtils.get_categories_collection(db)
        query = CategoryUtils.build_category_query(category_id=category_id)
        results = CategoryUtils.get_categories(categories_collection, query=query, page_num=page_num_int, page_size=page_size)
        results = list(results)
        
        output = CategoryList(page_number=page_num_int, page_size=page_size, categories=[])
        for category in results:
            print(category)
            if isinstance(output.categories, list):
                try:
                    output.categories.append(
                        {
                            "category_id": category["category_id"],
                            "category_name": category["category_name"]
                        }
                    )
                except KeyError:
                    logging.getLogger(__name__).warning(f"Failed to get document {category}. Unexpected structure")
        
        client.close()
        return output
