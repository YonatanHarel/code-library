import yaml
from pydantic import BaseModel



class MongoSettings(BaseModel):
    uri: str = "mongodb://localhost:27017"
    database: str = "polydb"

class RedisSettings(BaseModel):
    uri: str = "redis://localhost:6379/0"
    namespace: str = "polydb"

class CLickHouseSettings(BaseModel):
    uri: str = "localhost"
    port: int = 9000
    database: str = "default"

class Settings(BaseModel):
    backend: str = "mongodb" # mongodb | redis | clickhouse
    mongo: MongoSettings = MongoSettings()
    redis: RedisSettings = RedisSettings()
    clickhouse: CLickHouseSettings = CLickHouseSettings()

def load_settings(path: str = "config.yaml") -> Settings:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    return Settings(**data)