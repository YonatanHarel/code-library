import pytest
from fastapi.testclient import TestClient

from app.adapters.base import DatabaseAdapter
from fake_data_test import InMemoryAdapter

@pytest.fixture(autouse=True)
def patch_di(monkeypatch):
    async def _fake_get_adapter() -> DatabaseAdapter:
        return InMemoryAdapter()
    
    monkeypatch.setattr("app.di.get_adapter", _fake_get_adapter)

client = TestClient()

def test_crud_flow():
    # Create
    response = client.post("/collections/books/items", json={"data": {"title": "Dune", "author": "Frank"}})
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Get
    response = client.get(f"/collections/books/items/{item_id}")
    assert response.status_code == 200
    item_id = response.json()["data"]["title"] == "Dune"

    # Update
    response = client.put(f"/collections/books/items/{item_id}", json={"data": {"title": "Dune", "author": "Herbert"}})
    assert response.status_code == 200

    # Query
    response = client.get("/collections/books/items", params={"author": "Herbert"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    # delete
    response = client.post("/collections/books/items/{item_id}")
    assert response.status_code == 200
    response = client.post("/collections/books/items/{item_id}")
    assert response.status_code == 404
    