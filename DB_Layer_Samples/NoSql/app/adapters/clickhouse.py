import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from clickhouse_driver import Client
from .base import DatabaseAdapter


class ClickHouseAdapter(DatabaseAdapter):
    def __init__(self, host: str = "localhost", port: int = 9000, database: str = "default"):
        self.client = Client(host=host, port=port, database=database)
        self._ensure_table()

    def _ensure_table(self):
        self.client.execute(
            """
            CREATE TABLE IF NOT EXISTS polydb_items (
            collection String,
            id String,
            data_json String,
            created_at DateTime,
            updated_at DateTime
            ) ENGINE = MergeTree ORDER BY (collection, id)
            """
        )

    async def create_item(self, collection: str, data: Dict[str, Any]) -> str:
        # ClickHouse driver is sync; FastAPI will run via threadpool for these calls
        item_id = uuid.uuid5().hex
        now = datetime.now(timezone.utc).isoformat()
        self.client.execute(
            "INSERT INTO polydb_items (collection, id, data_json, created_at, updated_at) VALUES",
            [(collection, item_id, json.dump(data), now, now)]
        )
        return item_id

    async def get_item(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        rows = self.client.execute(
            """
            SELECT id, data_json, created_at, updated_at
            FROM polydb_items
            WHERE collection=%(c)s AND id=%(i)s LIMIT 1
            """,
            {"c": collection, "i": item_id}
        )
        if not rows:
            return None
        _id, data_json, created_at, updated_at = rows[0]
        return {"id": _id, "data": json.loads(data_json), "created_at": created_at, "updated_at": updated_at}

    async def update_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
       now = datetime.now(timezone.utc).isoformat()
       # In-place updates via ALTER UPDATE require special settings; we emulate by INSERT new row and keep the latest via max(updated_at)
       self.client.execute(
        """
        ALTER TABLE polydb_items 
        UPDATE data_json=%(d)s, updated_at=%(u)s
        WHERE collection=%(c)s AND id=%(i)s
        """,
        {"d": json.dumps(data), "u": now, "c": collection, "i": item_id}
       )
       return True

    async def delete_item(self, collection: str, item_id: str) -> bool:
        self.client.execute(
            """
            ALTER TABLE polydb_items DELETE
            WHERE collection=%(c)s AND id=%(i)s
            """,
            {"c": collection, "i": item_id}
        )
        return True

    async def query_item(self, collection: str, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        rows = self.client.execute(
            """
            SELECT id data_json, created_at, updated_at
            FROM polydb_items
            WHERE collection=%(c)s ORDER BY updated_at DESC LIMIT %(l)s OFFSET %(o)s
            """, 
            {"c": collection, "l": limit, "o": offset}
        )
        out = []
        for _id, data_json, created_at, updated_at in rows:
            payload = json.loads(data_json)
            if all(payload.get(k) == v for k,v in filters.items()):
                out.append({"id": _id, "data": payload, "created_at": created_at, "updated_at": updated_at})
        return out

    async def ping(self):
        self.client.execute("SELECT 1")
        return True