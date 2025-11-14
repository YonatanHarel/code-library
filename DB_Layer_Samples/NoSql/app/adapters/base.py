from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class DatabaseAdapter(ABC):
    @abstractmethod
    async def create_item(self, collection: str, data: Dict[str, Any]) -> str:
        ...
    
    @abstractmethod    
    async def get_item(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    async def update_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def delete_item(self, collection: str, item_id: str) -> bool:
        ...

    @abstractmethod
    async def query_item(self, collection: str, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        ...
        
    @abstractmethod
    async def ping(self) -> bool:
        ...