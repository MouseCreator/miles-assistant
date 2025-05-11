
from collections.abc import Callable
from typing import List

from src.miles.core.context.flags import Flags
from src.miles.core.context.text_recognize_context import TextRecognizeContext


class TextDataHolder:
    def __init__(self, text: List[str]):
        self._text = text

    def size(self) -> int:
        return len(self._text)

    def create_context(self,
                       on_interrupt: Callable[[TextRecognizeContext], None],
                       start_at: int,
                       flags: Flags,
                       failed: bool = False):
        return TextRecognizeContext(
            tokens=self._text, on_interrupt=on_interrupt, start_at=start_at, failed=failed, flags=flags
        )
