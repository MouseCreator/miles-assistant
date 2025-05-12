from typing import Self, List

from src.miles.core.context.data_context import RecognizeContext
from src.miles.core.context.data_holder import TextDataHolder
from src.miles.core.context.flags import Flags
from src.miles.core.normalized.history import NorHistory, HistoryItem
from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer
from src.miles.core.recognizer.normalized_matcher import NormalizedState, NormalizedNode


class RecPointer:

    _history: NorHistory
    _of_data: TextDataHolder

    def __init__(self,
                 at_state: NormalizedState,
                 of_data: TextDataHolder,
                 current_position = 0,
                 history: NorHistory | None = None,
                 flags: Flags | None = None):
        self._at_state = at_state

        self._current_position = current_position
        self._of_data = of_data

        if history is None:
            history = NorHistory()
        self._history = history

        if flags is None:
            flags = Flags()
        self._flags = flags

    def __eq__(self, other):
        if not isinstance(other, RecPointer):
            return False
        return self._at_state == other._at_state and self._history == other._history

    def __str__(self):
        return f"Pointer {self._at_state}"

    def get_state(self) -> NormalizedState:
        return self._at_state

    def move_to(self, state: NormalizedState) -> Self:
        return RecPointer(
            at_state=state,
            of_data=self._of_data,
            current_position=self._current_position,
            history=self._history,
            flags=self._flags.copy()
        )
    def get_position(self):
        return self._current_position
    def _create_next_pointer(self, context: RecognizeContext, node: NormalizedNode) -> Self:
        new_position = context.index()

        new_item = HistoryItem(
            node=node,
            prev_point=self._current_position,
            included=context.get_consumed(),
            next_point=new_position
        )
        return RecPointer(
            at_state=self._at_state,
            of_data=self._of_data,
            current_position=new_position,
            history=self._history.extend(new_item)
        )

    def advance_with_analyzer(self, node : NormalizedNode, analyzer: GenericContextAnalyzer) -> List[Self]:
        result_pointers: List[RecPointer] = []
        def _on_interrupt(ctx: RecognizeContext):
            if ctx.is_failed():
                return
            next_pointer = self._create_next_pointer(ctx, node)
            if next_pointer is not None:
                result_pointers.append(next_pointer)

        context: RecognizeContext = self._of_data.create_context(_on_interrupt, self._current_position, flags=self._flags)
        analyzer.process(context)
        _on_interrupt(context)
        return result_pointers

    def is_finished(self):
        return self._at_state.is_final() and self._current_position >= self._of_data.size()

    def get_history(self) -> NorHistory:
        return self._history

    def flags(self):
        return self._flags