from typing import List, Callable, Self, TypeVar

from src.miles.shared.context.flags import Flags
from src.miles.core.recognizer.recognizer_stack import RecognizerStack
from src.miles.shared.context.shared_node import SharedNode

T = TypeVar('T')

class ConsumedRange:
    def __init__(self, from_index: int, to_index: int):
        self.from_index = from_index
        self.to_index = to_index

    def as_range(self) -> range:
        return range(self.from_index, self.to_index)

    def apply_to(self, lst: List[T]) -> List[T]:
        return lst[self.from_index : self.to_index]



class TextRecognizeContext:
    def flags(self) -> Flags:
        return self._flags

    _tokens: List[str]
    _flags: Flags
    _consumed: List[str]
    _stack: RecognizerStack
    _last_certainty: float

    def __init__(self,
                 tokens: List[str],
                 on_interrupt: Callable[[Self], None],
                 node: SharedNode,
                 start_at=0,
                 failed=False,
                 flags: Flags|None = None,
                 stack: RecognizerStack|None = None):
        self._tokens = list(tokens)
        self._position = start_at
        self._total = len(self._tokens)
        self._fail_flag = failed
        self._on_interrupt = on_interrupt
        self._consumed = []
        self._node = node
        self._last_certainty = 0.0
        if stack is None:
            stack = RecognizerStack()
        self._stack = stack
        if flags is None:
            flags = Flags()
        self._flags = flags.copy()

    def current(self) -> str | None:
        if self.is_empty():
            return None
        return self._tokens[self._position]

    def index(self):
        return self._position

    def lookahead(self, items: int) -> List[str]:
        return self._tokens[self._position:self._position + items]

    def interrupt(self):
        self._on_interrupt(self)

    def consume(self, items:int = 1, interrupted: bool = False, certainty: float=100) -> None:
        if self._fail_flag:
            return
        c_range = ConsumedRange(self._position, self._position + items)
        self._consumed.extend(c_range.apply_to(self._tokens))
        self._position = min(self._total, self._position + items)
        self._last_certainty = certainty
        if interrupted:
            self.interrupt()

    def variant(self, items: int = 1, certainty: float=100) -> None:
        prev_position = self._position
        prev_consumed = list(self._consumed)
        prev_certainty = self._last_certainty

        c_range = ConsumedRange(self._position, self._position + items)
        self._consumed.extend(c_range.apply_to(self._tokens))
        self._position = min(self._total, self._position + items)
        self._last_certainty = certainty

        self.interrupt()

        self._last_certainty = prev_certainty
        self._position = prev_position
        self._consumed = prev_consumed

    def ignore(self, items: int = 1, interrupted: bool = False, certainty: float=100) -> None:
        self._position = min(self._total, self._position + items)
        self._last_certainty = certainty
        if interrupted:
            self.interrupt()

    def last_certainty(self):
        return self._last_certainty
    def remaining_count(self) -> int:
        return self._total - self._position

    def has_any(self) -> bool:
        return self._position < self._total

    def is_empty(self) -> bool:
        return self._position >= self._total

    def is_failed(self):
        return self._fail_flag

    def fail(self):
        self._fail_flag = True

    def all_tokens(self) -> List[str]:
        return list(self._tokens)

    def write(self, items: List[str]) -> None:
        self._consumed.extend(items)

    def get_consumed(self) -> List[str]:
        return self._consumed

    def position(self) -> int:
        return self._position

    def stack(self):
        return self._stack

    def set_flags(self, flags: Flags):
        self._flags = flags

    def node(self) -> SharedNode:
        return self._node