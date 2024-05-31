from datetime import datetime
from typing import List
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        product_model = ProductModel(**body.model_dump())
        await self.collection.insert_one(product_model.model_dump())
        return ProductOut(**product_model.model_dump())

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with ID: {id}")
        return ProductOut(**result)

    async def query(self, price_range_filter: bool) -> List[ProductOut]:
        filter_query = {"price": {"$gt": 5000, "$lt": 8000}} if price_range_filter else {}
        products = [ProductOut(**item) async for item in self.collection.find(filter=filter_query)]
        return products

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        update_data = {
            "$set": {
                **body.model_dump(exclude_none=True),
                "updated_at": datetime.now(),
            }
        }
        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update=update_data,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        if not result:
            raise NotFoundException(message=f"Product not found with ID: {id}")
        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(message=f"Product not found with ID: {id}")
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0


product_usecase = ProductUsecase()
