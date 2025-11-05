from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from openapi_server.apis.products_api_base import BaseProductsApi
from openapi_server.models.product import Product
from openapi_server.models.product_create import ProductCreate
from openapi_server.models.product_update import ProductUpdate
from openapi_server.db import get_collection


class ProductsApiImpl(BaseProductsApi):
	def _to_product_model(self, doc: dict) -> Product:
		"""Convert a MongoDB document to Product model."""
		if not doc:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

		return Product(
			id=int(doc["id"]),
			name=doc["name"],
			price=doc["price"],
			stock=doc["stock"],
			description=doc.get("description"),
			createdAt=doc.get("createdAt", datetime.utcnow()),
			updatedAt=doc.get("updatedAt", datetime.utcnow()),
		)

	async def _next_product_id(self) -> int:
		"""Generate next incremental integer id based on current max id."""
		col = get_collection("products")
		doc = await col.find_one(sort=[("id", -1)])
		if not doc or "id" not in doc:
			return 1
		try:
			return int(doc["id"]) + 1
		except Exception:
			# Fallback if stored as string
			return 1

	async def create_product(self, product_create: ProductCreate) -> Product:
		products = get_collection("products")

		new_id = await self._next_product_id()
		now = datetime.utcnow()

		doc = {
			"id": new_id,
			"name": product_create.name,
			"price": product_create.price,
			"stock": product_create.stock if product_create.stock is not None else 0,
			"description": product_create.description,
			"createdAt": now,
			"updatedAt": now,
		}

		await products.insert_one(doc)
		return self._to_product_model(doc)

	async def get_product(self, id: int) -> Product:
		products = get_collection("products")
		doc = await products.find_one({"id": int(id)})
		if not doc:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
		return self._to_product_model(doc)

	async def replace_product(self, id: int, product_create: ProductCreate) -> Product:
		products = get_collection("products")
		existing = await products.find_one({"id": int(id)})
		if not existing:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

		now = datetime.utcnow()
		# Preserve createdAt if exists
		created_at = existing.get("createdAt", now)

		replacement = {
			"id": int(id),
			"name": product_create.name,
			"price": product_create.price,
			"stock": product_create.stock if product_create.stock is not None else 0,
			"description": product_create.description,
			"createdAt": created_at,
			"updatedAt": now,
		}

		await products.replace_one({"id": int(id)}, replacement)
		return self._to_product_model(replacement)

	async def delete_product(self, id: int) -> None:
		products = get_collection("products")
		result = await products.delete_one({"id": int(id)})
		if result.deleted_count == 0:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
		return None

	async def update_product(self, id: int, product_update: ProductUpdate) -> Product:
		products = get_collection("products")
		existing = await products.find_one({"id": int(id)})
		if not existing:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

		updates = {}
		if product_update.name is not None:
			updates["name"] = product_update.name
		if product_update.price is not None:
			updates["price"] = product_update.price
		if product_update.stock is not None:
			updates["stock"] = product_update.stock
		if product_update.description is not None:
			updates["description"] = product_update.description

		updates["updatedAt"] = datetime.utcnow()

		if updates:
			await products.update_one({"id": int(id)}, {"$set": updates})

		# Fetch updated doc
		doc = await products.find_one({"id": int(id)})
		return self._to_product_model(doc)

