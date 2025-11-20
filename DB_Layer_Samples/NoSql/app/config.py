import yaml
from pydantic import BaseModel



class MongoSettings(BaseModel):
    uri: str = "mongodb://mongo:27017"
    database: str = "polydb"

class RedisSettings(BaseModel):
    uri: str = "redis://redis:6379/0"
    namespace: str = "polydb"

class ClickHouseSettings(BaseModel):
    uri: str = "localhost"
    port: int = 9000
    database: str = "default"

class Settings(BaseModel):
    backend: str = "mongodb" # mongodb | redis | clickhouse
    mongo: MongoSettings = MongoSettings()
    redis: RedisSettings = RedisSettings()
    clickhouse: ClickHouseSettings = ClickHouseSettings()

def load_settings(path: str = "config.yaml") -> Settings:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    return Settings(**data)