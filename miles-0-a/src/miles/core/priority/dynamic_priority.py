from abc import ABC, abstractmethod
from typing import List

from src.miles.core.context.flags import Flags
from src.miles.core.matcher.matcher import ConnectionType


class DynamicPriorityContext:
    def __init__(self,
                 tokens: List[str],
                 connection_type: ConnectionType,
                 connection_argument: str,
                 static_priority: int,
                 start_at=0,
                 flags=Flags | None
                 ):
        self._tokens = list(tokens)
        self._position = start_at
        self._total = len(self._tokens)
        self._connection_type = connection_type
        self._connection_argument = connection_argument
        self._connection_priority = static_priority
        if flags is None:
            flags = Flags()
        self.flags = flags.copy()

    def __len__(self):
        return self._total

    def connection_type(self):
        return self._connection_type

    def connection_argument(self):
        return self._connection_argument

    def static_priority(self):
        return self.static_priority()

    def is_empty(self):
        return self._position >= self._total

    def current(self) -> str | None:
        if self.is_empty():
            return None
        return self._tokens[self._position]

    def index(self):
        return self._position

    def lookahead(self, items: int) -> List[str]:
        return self._tokens[self._position: self._position + items]


class DynamicPriorityRule(ABC):
    @abstractmethod
    def plugin(self) -> str:
        pass

    @abstractmethod
    def is_applicable(self, context: DynamicPriorityContext) -> bool:
        pass

    @abstractmethod
    def priority(self, context: DynamicPriorityContext) -> int:
        pass