from abc import ABC, abstractmethod
from typing import List

from src.miles.core.recognizer.normalized_matcher import HistoryNodeType
from src.miles.shared.context.flags import Flags


class DynamicPriorityContext:
    def __init__(self,
                 tokens: List[str],
                 connection_type: HistoryNodeType,
                 connection_argument: str,
                 connection_name: str,
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
        self._connection_name = connection_name
        if flags is None:
            flags = Flags()
        self.flags = flags.copy()

    def __len__(self):
        return self._total

    def is_word(self):
        return self._connection_type == HistoryNodeType.WORD

    def argument(self):
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

    def is_matching(self):
        return self._connection_type == HistoryNodeType.MATCHING

    def is_automatic(self):
        return self._connection_type == HistoryNodeType.AUTOMATIC


class DynamicPriorityRule(ABC):

    @abstractmethod
    def is_applicable(self, context: DynamicPriorityContext) -> bool:
        pass

    @abstractmethod
    def priority(self, context: DynamicPriorityContext) -> int:
        pass

    def ordered(self):
        return 0

class DynamicPriorityRuleSet:
    def __init__(self):
        self._rules = []
    def append(self, rule: DynamicPriorityRule):
        self._rules.append(rule)
    def extend(self, rules: List[DynamicPriorityRule]):
        self._rules.extend(rules)
    def get_rules(self) -> List[DynamicPriorityRule]:
        return list(self._rules)