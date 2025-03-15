from typing import List, Self

from src.miles.core.matcher.matcher import MatchState, MatchConnection
from src.miles.utils.decorators import auto_str

@auto_str
class HistoryItem:
    def __init__(self,
                 prev_state: MatchState,
                 connection: MatchConnection,
                 prev_point: int,
                 included: List[int],
                 next_point: int):
        self.prev_state = prev_state
        self.connection = connection
        self.prev_point = prev_point
        self.included = included
        self.next_point = next_point

    def __eq__(self, other):
        if not isinstance(other, HistoryItem):
            return False
        return (
                self.prev_state == other.prev_state
                and self.connection == other.connection
                and self.prev_point == other.prev_point
                and self.included == other.included
                and self.next_point == other.next_point
                )

    def __str__(self):
        return super().__str__()

@auto_str
class RecHistory:
    _items: List[HistoryItem]
    def __init__(self, items: List[HistoryItem] | None=None):
        if items is None:
            self._items = []
        else:
            self._items = list(items)

    def extend(self, item: HistoryItem) -> Self:
        return RecHistory(self._items + [item])

    def all_items(self):
        return list(self._items)
    def __eq__(self, other):
        if not isinstance(other, RecHistory):
            return False
        return self._items == other._items