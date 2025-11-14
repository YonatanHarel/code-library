from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field  # type: ignore[import]


class ItemCreate(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)
    
class ItemUpdate(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)

class Item(BaseModel):
    id: str
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime