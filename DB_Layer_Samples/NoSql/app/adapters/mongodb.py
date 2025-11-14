from datetime import datetime
from bson import ObjectId  # type: ignore[import]
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore[import]

from typing import Any, Dict, List, Optional

from .base import DatabaseAdapter


class MongoAdapter(DatabaseAdapter):
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        
    async def create_item(self, collection: str, data: Dict[str, Any]) -> str:
        now = datetime.utcnow()
        doc = {"data": data, "created_at": now, "updated_at":now}
        res = await self.db[collection].insert_one(doc)
        return str(res.inserted_id)

    async def get_item(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db[collection].find_one({"id": ObjectId(item_id)})
        if not doc:
            return None
        return {
            "id": str(doc["_id"]),
            "data": doc.get("data", {}),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at")
        }

    async def update_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        now = datetime.now()
        res = await self.db[collection].update_one({"_id": ObjectId(item_id)})
        return res.modified_count > 0

    async def delete_item(self, collection: str, item_id: str) -> bool:
        res = await self.db[collection].delete_one({"_id": ObjectId(item_id)})
        return res.deleted_count > 0

    async def query_item(self, collection: str, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = self.db[collection].find({"data": {"$exists": True}, **{f"data.{k}": v for k,v in filters.items()}}).skip(offset).limit(limit)
        out = []
        async for doc in cursor:
            out.append({
                "id": str(doc["_id"]),
                "data": doc.get("data", {}),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
            })
        return out

    async def ping(self) -> bool:
        await self.db.command("ping")
        return True