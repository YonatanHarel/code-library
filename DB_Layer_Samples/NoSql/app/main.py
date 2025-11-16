from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Query

from .adapters.base import DatabaseAdapter
from .di import get_adapter
from .models import Item, ItemCreate, ItemUpdate

app = FastAPI(title="PolyDB API", version="0.1.0")

@app.get("/health")
async def health(adapter: DatabaseAdapter = Depends(get_adapter)):
    ok = await adapter.ping()
    return {"ok": ok}

@app.post("/collection/{collection}/items", response_model=Dict[str, str])
async def create_item(collection: str, payload: ItemCreate, adapter: DatabaseAdapter = Depends(get_adapter)):
    item_id = await adapter.create_item(collection, payload.data)
    return {"id": item_id}

@app.get("/collection/{collection}/items/{item_id}")
async def get_item(collection: str, item_id: str, adapter: DatabaseAdapter = Depends(get_adapter)):
    doc = await adapter.get_item(collection, item_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return Item(id=doc["id"], data=doc["data"], created_at=doc["created_at"], updated_at=doc["updated_at"])

@app.put("/collection/{collection}/items/{item_id}")
async def update_item(collection: str, item_id: str, payload: ItemUpdate, adapter: DatabaseAdapter = Depends(get_adapter)):
    ok = await adapter.update_item(collection, item_id, payload.data)
    if not ok:
        raise HTTPException(status_code=404, detail="Failed to update item")
    return {"ok": True}

@app.delete("/collection/{collection}/items/{item_id}")
async def delete_item(collection: str, item_id: str, adapter: DatabaseAdapter = Depends(get_adapter)):
    ok = await adapter.delete_item(collection, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}

@app.get("/collection/{collection}/items", response_model=List[Item])
async def list_items(collection: str, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), adapter: DatabaseAdapter = Depends(get_adapter), **filters: Any):
    docs = await adapter.query_item(collection, filters, limit, offset)
    return [Item(id=d["id"], data=d["data"], created_at=d["created_at"], updated_at=d["updated_at"]) for d in docs]