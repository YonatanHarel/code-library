from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from app.adapters.base import DatabaseAdapter


class InMemoryAdapter(DatabaseAdapter):
    def __init__(self):
        self.store: Dict[str, Dict[str, Dict[str, Any]]] = {}

    async def create_item(self, collection: str, data: Dict[str, Any]) -> str:
        col = self.store.setdefault(collection, {})
        item_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        col[item_id] = {"id": item_id, "data": data, "created_at": now, "updated_at": now}
        return item_id

    async def get_item(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get(collection, {}).get(item_id)

    async def update_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        col = self.store.get(collection, {})
        if item_id not in col:
            return False
        col[item_id]["data"] = data
        col[item_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return True
    
    async def delete_item(self, collection: str, item_id: str) -> bool:
        col = self.store.get(collection, {})
        return col.pop(item_id, None) is not None

    async def query_item(self, collection: str, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        items = list(self.store.get(collection, {}).values())
        out = []
        for item in items:
            if all(item["data"].get(k) == v for k, v in filters.items()):
                out.append(item)
        return out[offset:offset+limit]

    async def ping(self) -> bool:
        return True