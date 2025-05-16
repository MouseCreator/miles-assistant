from typing import List, Self


class RecStackItem:
    def __init__(self, title: str, position: int):
        self.title = title
        self.position = position
    def __eq__(self, other):
        if not isinstance(other, RecStackItem):
            return False
        return self.position == other.position and self.title == other.title

class RecognizerStack:
    _stack: List[RecStackItem]
    def __init__(self, items: List[RecStackItem] | None = None):
        if items is None:
            items = []
        self._stack = items

    def push(self, title: str, position: int) -> None:
        item = RecStackItem(title, position)
        self._stack.append(item)

    def contains(self, title: str, position: int) -> bool:
        return RecStackItem(title, position) in self._stack

    def copy(self) -> Self:
        return RecognizerStack(list(self._stack))