from abc import ABC, abstractmethod
from typing import List, Any, TypeVar, Optional, Type

from src.miles.core.context.flags import Flags


class ConsumedRange:
    def __init__(self, from_index: int, to_index: int):
        self.from_index = from_index
        self.to_index = to_index

    def as_range(self) -> range:
        return range(self.from_index, self.to_index)


class RecognizeContext(ABC):
    @abstractmethod
    def interrupt(self) -> None:
        pass
    @abstractmethod
    def consume(self, items: int = 1, interrupted: bool = False) -> None:
        pass
    @abstractmethod
    def ignore(self, items: int = 1, interrupted: bool = False) -> None:
        pass
    @abstractmethod
    def variant(self, items: int = 1) -> None:
        pass
    @abstractmethod
    def index(self) -> int:
        pass
    @abstractmethod
    def get_consumed(self) -> List[int]:
        pass
    @abstractmethod
    def get_consumed_ranges(self) -> List[ConsumedRange]:
        pass
    @abstractmethod
    def is_failed(self):
        pass
    @abstractmethod
    def fail(self):
        pass
    @abstractmethod
    def remaining_count(self) -> int:
        pass
    @abstractmethod
    def has_any(self) -> bool:
        pass
    @abstractmethod
    def is_empty(self) -> bool:
        pass
    @abstractmethod
    def flags(self) -> Flags:
        pass


