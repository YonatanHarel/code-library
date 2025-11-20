import json
import uuid
import redis
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .base import DatabaseAdapter


class RedisAdapter(DatabaseAdapter):
    def __init__(self, uri:str, namespace:str = "redisdb"):
        self.uri = uri
        self.namespace = namespace
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.uri, decode_response=True)
        return self._client

    def _key(self, collection: str, item_id: str) -> str:
        return f"{self.namespace}:{collection}:{item_id}"

    async def create_item(self, collection: str, data: Dict[str, Any]) -> str:
        client = await self._get_client()
        item_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        payload = {"id": item_id, "data": data, "created_at": now, "updated_at": now}
        await client.set(self._key(collection, item_id), json.dumps(payload))
        await client.sadd(f"{self.namespace}:{collection}:ids", item_id)
        return item_id

    async def get_item(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        raw = await client.get(self._key(collection, item_id))
        return json.loads(raw) if raw else None

    async def update_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        client = await self._get_client()
        raw = await client.get(self._key(collection, item_id))
        if not raw:
            return False
        doc = json.loads(raw)
        doc["data"] = data
        doc["updated_at"] = datetime.now(timezone.utc).isoformat()
        await client.set(self._key(collection, item_id), json.dumps(doc))
        return True

    async def delete_item(self, collection: str, item_id: str) -> bool:
        client = await self._get_client()
        removed = await client.delete(self._key(collection, item_id))
        if removed:
            await client.srem(f"{self.namespace}:{collection}:ids", item_id)
        return removed == 1

    async def query_item(self, collection: str, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        client = await self._get_client()
        ids = list(await client.smembers(f"{self.namespace}:{collection}:ids"))
        ids.sort()
        results: List[Dict[str, Any]] = []
        for item_id in ids[offset:offset + limit]:
            raw = await client.get(self._key(collection, item_id))
            if not raw:
                continue
            doc = json.loads(raw)
            if all(doc.get("data", {}).get(k) == v for k,v in filters.items()):
                results.append(doc)
        return results

    async def ping(self) -> bool:
        client = await self._get_client()
        return await client.ping()