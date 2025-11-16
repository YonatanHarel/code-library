# PolyDB (Python / FastAPI)
docker compose up -d # launches Mongo/Redis/ClickHouse and the API container
# OR run API directly
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```


Visit: http://localhost:8000/docs


## Switch backends


Edit `config.yaml` and set `backend: mongodb|redis|clickhouse`. No code changes needed.


## Quick demo (Mongo default)


```bash
curl -s -X POST http://localhost:8000/collections/users/items -H 'Content-Type: application/json' -d '{"data": {"name": "Noa", "age": 31}}'
# => {"id": "..."}


curl -s http://localhost:8000/collections/users/items?name=Noa | jq
```


## Tests


```bash
pytest -q
```


## Notes
- ClickHouse is columnar; here it stores JSON strings for simplicity.
- Adapters follow a minimal CRUD + query contract; extend as needed.
- For production, secure inputs, enable auth, add pagination cursors, and proper logging.