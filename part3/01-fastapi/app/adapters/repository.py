from typing import List, Optional
from uuid import UUID

from app.domain.models import Order


class Repository:
    def get(self, ref: UUID) -> Order:
        pass

    def add(self, entity: Order) -> UUID:
        pass

    def get_all(self) -> List[Order]:
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._items: List[Order] = []

    def get_all(self) -> List[Order]:
        return self._items

    def get(self, ref: UUID) -> Optional[Order]:
        return next((item for item in self._items if item.id == ref), None)

    def add(self, entity: Order) -> UUID:
        self._items.append(entity)
        new_item = self.get(entity.id)
        if not new_item:
            raise ValueError
        return new_item.id
