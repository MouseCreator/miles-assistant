from collections.abc import Callable
from typing import List

from src.miles.core.recognizer.normalized_matcher import HistoryNodeType
from src.miles.core.recognizer.recognizer_stack import RecognizerStack
from src.miles.shared.context.flags import Flags
from src.miles.shared.context.shared_node import SharedNode
from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.priority.dynamic_priority import DynamicPriorityContext


class TextDataHolder:
    def __init__(self, text: List[str]):
        self._text = text

    def __str__(self):
        return f"{str(self._text)}"

    def size(self) -> int:
        return len(self._text)

    def create_context(self,
                       on_interrupt: Callable[[TextRecognizeContext], None],
                       start_at: int,
                       flags: Flags,
                       stack: RecognizerStack,
                       node: SharedNode,
                       failed: bool = False):
        return TextRecognizeContext(
            tokens=self._text,
            on_interrupt=on_interrupt,
            start_at=start_at,
            failed=failed,
            flags=flags,
            node=node,
            stack=stack
        )

    def dynamic_priority_context(self,
                                 start_at: int,
                                 flags: Flags,
                                 connection_type: HistoryNodeType,
                                 connection_arg: str,
                                 connection_name: str,
                                 priority: int):
        return DynamicPriorityContext(
            tokens=self._text,
            connection_type=connection_type,
            connection_argument=connection_arg,
            connection_name=connection_name,
            static_priority=priority,
            start_at=start_at,
            flags=flags
        )

    def full(self):
        return ' '.join(self._text)

    def __getitem__(self, item):
        return self._text[item]
