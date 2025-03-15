from typing import List, Self

from src.miles.core.matcher.matcher import MatchState, MatchConnection


class HistoryItem:
    def __init__(self,
                 prev_state: MatchState,
                 connection: MatchConnection,
                 prev_point: int,
                 step: int):
        self.prev_state = prev_state
        self.connection = connection
        self.prev_point = prev_point
        self.step = step

    def __eq__(self, other):
        if not isinstance(other, HistoryItem):
            return False
        return (
                self.prev_state == other.prev_state
                and self.connection == other.connection
                and self.prev_point == other.prev_point
                and self.step == other.step
                )

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