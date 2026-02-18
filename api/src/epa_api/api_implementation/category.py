from fastapi.exceptions import HTTPException
from epa_api.apis.category_api import BaseCategoryApi
from epa_api.models.category_list import CategoryList
from epa_api.models.subscribe_category_request import SubscribeCategoryRequest
from typing import Optional
from pydantic import StrictStr
from epa_api.api_implementation.utils.token import TokenUtils
from epa_api.api_implementation.utils.category import CategoryUtils
from epa_api.api_implementation.utils.mongo import MongoUtils

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
        output = CategoryUtils.get_category_list(list(results), page_num=page_num_int, page_size=page_size)
        
        client.close()
        return output
        
    async def subscribe_to_category(
        self,
        subscribe_category_request: SubscribeCategoryRequest,
    ) -> None:
        """Subscribe a user to a category"""
        
        token = TokenUtils.validate_access_token_with_db()
        user_id = TokenUtils.get_user_id(token)
        
        client, db = MongoUtils.get_mongodb_database_connection()
        category_collection = MongoUtils.get_categories_collection(db)
        user_collection = MongoUtils.get_user_collection(db)
        
        try:
            CategoryUtils.validate_subscribe_category_request(
                subscribe_category_request,
                user_id,
                category_collection,
                user_collection
            )
        except HTTPException as e:
            client.close()
            raise e
            
        CategoryUtils.subscribe_user_to_category(user_id, user_collection, subscribe_category_request.category_id)
        client.close()
        
    async def unsubcribed_user_from_category(
        self,
        subscribe_category_request: SubscribeCategoryRequest,
    ) -> None:
        """Unsubscribe a user from a category"""
        
        token = TokenUtils.validate_access_token_with_db()
        user_id = TokenUtils.get_user_id(token)
        
        client, db = MongoUtils.get_mongodb_database_connection()
        category_collection = MongoUtils.get_categories_collection(db)
        user_collection = MongoUtils.get_user_collection(db)
        
        try:
            CategoryUtils.validate_unsubscribe_category_request(
                subscribe_category_request,
                user_id,
                category_collection,
                user_collection
            )
        except HTTPException as e:
            client.close()
            raise e
            
        CategoryUtils.unsubscribe_user_from_category(user_id, user_collection, subscribe_category_request.category_id)
        client.close()
        
    async def get_user_subscribed_categories(
        self,
        page_num:Optional[StrictStr],
    ) -> CategoryList:
        """Get users subscribed categories"""
        
        token = TokenUtils.validate_access_token_with_db()
        user_id = TokenUtils.get_user_id(token)
        
        client, db = MongoUtils.get_mongodb_database_connection()
        category_collection = MongoUtils.get_categories_collection(db)
        user_collection = MongoUtils.get_user_collection(db)
        
        page_num_int = CategoryUtils.get_page_num_from_string(page_num)
        page_size = CategoryUtils.get_page_size()
        results = CategoryUtils.get_user_subscribed_categories(
            user_id, 
            user_collection, 
            category_collection,
            page_num_int,
            page_size
        )
        
        if not results:
            results = []
        else:
            results = list(results)
            
        output = CategoryUtils.get_category_list(results, page_num=page_num_int, page_size=len(results))
        
        client.close()
        return output
