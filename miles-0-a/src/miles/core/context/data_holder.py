from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List

from src.miles.core.context.data_context import RecognizeContext
from src.miles.core.context.data_types import InputDataType
from src.miles.core.context.recognize_context import TextRecognizeContext


class InputDataHolder(ABC):
    @abstractmethod
    def type(self) -> InputDataType:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def create_context(self,
                       on_interrupt: Callable[[RecognizeContext], None],
                       start_at: int,
                       failed: bool = False):
        pass

class TextDataHolder(InputDataHolder):

    def __init__(self, text: List[str]):
        self._text = text

    def type(self) -> InputDataType:
        return InputDataType.TEXT

    def size(self) -> int:
        return len(self._text)

    def create_context(self,
                       on_interrupt: Callable[[TextRecognizeContext], None],
                       start_at: int,
                       failed: bool = False):
        return TextRecognizeContext(
            tokens=self._text, on_interrupt=on_interrupt, start_at=start_at, failed=failed
        )
