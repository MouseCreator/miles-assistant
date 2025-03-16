from typing import List, Callable, Self

from src.miles.core.context.data_context import RecognizeContext, ConsumedRange


class TextRecognizeContext(RecognizeContext):

    _consumed: List[ConsumedRange]
    def __init__(self, tokens: List[str], on_interrupt: Callable[[Self], None], start_at=0, failed=False):
        self._tokens = list(tokens)
        self._position = start_at
        self._total = len(self._tokens)
        self._fail_flag = failed
        self._on_interrupt = on_interrupt
        self._consumed = []

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

    def consume(self, items:int = 1, interrupted: bool = False) -> None:
        self._consumed.append(ConsumedRange(self._position, self._position + items))
        self._position = min(self._total, self._position + items)
        if interrupted:
            self.interrupt()
    def variant(self, items: int = 1) -> None:
        prev_position = self._position
        prev_consumed = list(self._consumed)

        self._consumed.append(ConsumedRange(self._position, self._position + items))
        self._position = min(self._total, self._position + items)
        self.interrupt()

        self._position = prev_position
        self._consumed = prev_consumed
    def ignore(self, items: int = 1, interrupted: bool = False) -> None:
        self._position = min(self._total, self._position + items)
        if interrupted:
            self.interrupt()

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

    def get_consumed(self) -> List[int]:
        lst = []
        for r in self.get_consumed_ranges():
            lst.extend(r.as_range())
        return lst

    def get_consumed_ranges(self) -> List[ConsumedRange]:
        return list(self._consumed)