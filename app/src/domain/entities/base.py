from dataclasses import dataclass
from typing import Generic, TypeVar

ID = TypeVar("ID")


@dataclass
class Entity(Generic[ID]):
    id: ID


EntityType = TypeVar("EntityType", bound=Entity)
