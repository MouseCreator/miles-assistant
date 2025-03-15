from typing import List, Callable, Self


class RecognizeContext:

    def __init__(self, tokens: List[str], on_interrupt: Callable[[Self], None], start_at=0, failed=False):
        self._tokens = list(tokens)
        self._position = start_at
        self._total = len(self._tokens)
        self._fail_flag = failed
        self._on_interrupt = on_interrupt

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
