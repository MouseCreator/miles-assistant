from typing import List, Self

from src.miles.core.recognizer.normalized_matcher import NormalizedNode
from src.miles.utils.decorators import auto_str
from src.miles.utils.strings import print_list


@auto_str
class HistoryItem:
    def __init__(self,
                 node: NormalizedNode,
                 prev_point: int,
                 included: List[int],
                 next_point: int):
        self.node = node
        self.prev_point = prev_point
        self.included = included
        self.next_point = next_point

    def __eq__(self, other):
        if not isinstance(other, HistoryItem):
            return False
        return (
                self.node == other.node
                and self.prev_point == other.prev_point
                and self.included == other.included
                and self.next_point == other.next_point
                )

    def __str__(self):
        return super().__str__()
    def step(self) -> int:
        return self.next_point - self.prev_point

class NorHistory:
    _items: List[HistoryItem]
    def __init__(self, items: List[HistoryItem] | None=None):
        if items is None:
            self._items = []
        else:
            self._items = list(items)

    def extend(self, item: HistoryItem) -> Self:
        return NorHistory(self._items + [item])

    def all_items(self):
        return list(self._items)

    def __eq__(self, other):
        if not isinstance(other, NorHistory):
            return False
        return self._items == other._items
    def __str__(self):
        return print_list(self._items)

    def last(self) -> HistoryItem:
        return self._items[-1]