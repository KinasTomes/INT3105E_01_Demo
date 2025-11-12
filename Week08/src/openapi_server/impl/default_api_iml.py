from typing import Optional
from typing_extensions import Annotated
from pydantic import Field, StrictStr
from datetime import datetime
import math

from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.product_list_response import ProductListResponse
from openapi_server.models.product_list_response_meta import ProductListResponseMeta
from openapi_server.models.product import Product
from openapi_server.db import get_collection


class DefaultApiImpl(BaseDefaultApi):
    async def list_products(
        self,
        page: Optional[Annotated[int, Field(strict=True, ge=1)]] = 1,
        page_size: Optional[Annotated[int, Field(le=50, strict=True, ge=1)]] = 10,
        q: Annotated[Optional[StrictStr], Field(description="Optional name/keyword search")] = None,
    ) -> ProductListResponse:
        """
        List products with pagination and optional search
        
        Args:
            page: Page number (default: 1)
            page_size: Items per page (default: 10, max: 50)
            q: Optional search query for product name/description
            
        Returns:
            ProductListResponse with products and metadata
        """
        # Get MongoDB collection
        products_collection = get_collection("products")
        
        # Build query filter
        query_filter = {}
        if q:
            # Search in name and description (case-insensitive)
            query_filter = {
                "$or": [
                    {"name": {"$regex": q, "$options": "i"}},
                    {"description": {"$regex": q, "$options": "i"}}
                ]
            }
        
        # Get total count for pagination
        total_items = await products_collection.count_documents(query_filter)
        
        # Calculate pagination
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
        skip = (page - 1) * page_size
        
        # Fetch products from MongoDB
        cursor = products_collection.find(query_filter).skip(skip).limit(page_size).sort("createdAt", -1)
        products_data = await cursor.to_list(length=page_size)
        
        # Convert MongoDB documents to Product models
        products = []
        for doc in products_data:
            # MongoDB uses _id, but our model uses id
            product = Product(
                id=doc.get("id", doc.get("_id")),
                name=doc["name"],
                price=doc["price"],
                stock=doc["stock"],
                description=doc.get("description"),
                createdAt=doc.get("createdAt", doc.get("created_at", datetime.utcnow())),
                updatedAt=doc.get("updatedAt", doc.get("updated_at", datetime.utcnow()))
            )
            products.append(product)
        
        # Build metadata
        meta = ProductListResponseMeta(
            page=page,
            pageSize=page_size,
            totalItems=total_items,
            totalPages=total_pages
        )
        
        # Return response
        return ProductListResponse(
            data=products,
            meta=meta
        )
