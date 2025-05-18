from abc import ABC, abstractmethod
from typing import List

from src.miles.shared.context.flags import Flags
from src.miles.utils.decorators import auto_str


@auto_str
class CertaintyItem:
    def __init__(self, identity: int, origin: int, certainty: float, flags: Flags):
        self.identity = identity
        self.origin = origin
        self.certainty = certainty
        self.flags = flags


@auto_str
class CertaintyDecision:
    _all: List[List[CertaintyItem]]

    def __init__(self):
        self._all = []

    def add(self, items: List[CertaintyItem]):
        self._all.append(items)

    def plain(self) -> List[CertaintyItem]:
        result = []
        for i in self._all:
            result.extend(i)
        return result

    def size(self) -> int:
        return len(self._all)

    def get(self, i: int) -> List[CertaintyItem]:
        return self._all[i]

    def max_certainty(self):
        max_c = -1
        for lst in self._all:
            for item in lst:
                max_c = max(max_c, item.certainty)
        return max_c

    def get_by_certainty(self, certainty: float) -> List[CertaintyItem]:
        result = []
        for lst in self._all:
            for item in lst:
                if abs(item.certainty - certainty) < 1e-8:
                    result.append(item)
        return result

    def __iter__(self):
        return self._all.__iter__()


class CertaintyEffect(ABC):
    @abstractmethod
    def apply(self, decision: CertaintyDecision) -> List[CertaintyItem]:
        pass


class SortCertaintyEffect(CertaintyEffect):

    def apply(self, decision: CertaintyDecision) -> List[CertaintyItem]:
        items = decision.plain()
        return sorted(items, key=lambda p: p.certainty, reverse=True)


class OnlyMostCertainEffect(CertaintyEffect):
    def apply(self, decision: CertaintyDecision) -> List[CertaintyItem]:
        max_certainty = decision.max_certainty()
        return decision.get_by_certainty(max_certainty)


class OnePerGroupCertaintyEffect(CertaintyEffect):
    def apply(self, decision: CertaintyDecision) -> List[CertaintyItem]:
        result = []
        for group in decision:
            target = None
            for item in group:
                if target is None:
                    target = item
                elif item.certainty > target.certainty:
                    target = item
            if target is not None:
                result.append(target)
        return result
