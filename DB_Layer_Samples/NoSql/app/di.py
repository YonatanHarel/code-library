from .adapters.base import DatabaseAdapter
from .adapters.clickhouse import ClickHouseAdapter
from .adapters.mongodb import MongoAdapter
from .adapters.redisdb import RedisAdapter
from .config import CLickHouseSettings, load_settings


_settings = load_settings()

async def get_adapter() -> DatabaseAdapter:
    be = _settings.backend.lower()
    if be == "mongodb":
        return MongoAdapter(_settings.mongo.uri, _settings.mongo.database)
    if be == "redis":
        return RedisAdapter(_settings.redis.uri, _settings.redis.namespace)
    if be == "clickhouse":
        return ClickHouseAdapter(_settings.clickhouse.host, _settings.clickhouse.port, _settings.clickhouse.database)
    raise ValueError(f"Unsupported backend: {be}")