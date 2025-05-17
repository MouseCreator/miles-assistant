from typing import Self, List

from src.miles.core.recognizer.recognizer_stack import RecognizerStack
from src.miles.shared.context.data_holder import TextDataHolder
from src.miles.shared.context.flags import Flags
from src.miles.shared.context.shared_node import SharedNode
from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.core.normalized.history import NorHistory, HistoryItem
from src.miles.shared.context_analyzer import GenericContextAnalyzer
from src.miles.core.recognizer.normalized_matcher import NormalizedState, NormalizedNode, HistoryNodeType


class RecPointer:

    _history: NorHistory
    _of_data: TextDataHolder

    def __str__(self):
        return f'Pointer {{ {self._at_state}, {self._current_position} }}'

    def __init__(self,
                 at_state: NormalizedState,
                 of_data: TextDataHolder,
                 current_position = 0,
                 history: NorHistory | None = None,
                 flags: Flags | None = None,
                 stack: RecognizerStack | None = None,
                 certainty: float=100):
        self._at_state = at_state
        self._current_position = current_position
        self._certainty = certainty
        self._of_data = of_data

        if history is None:
            history = NorHistory()
        self._history = history

        if flags is None:
            flags = Flags()
        self._flags = flags

        if stack is None:
            stack = RecognizerStack()
        self._stack = stack

    def __eq__(self, other):
        if not isinstance(other, RecPointer):
            return False
        return self._at_state == other._at_state and self._history == other._history

    def get_state(self) -> NormalizedState:
        return self._at_state

    def certainty(self):
        return self._certainty

    def move_to(self, state: NormalizedState) -> Self:
        return RecPointer(
            at_state=state,
            of_data=self._of_data,
            current_position=self._current_position,
            history=self._history,
            flags=self._flags.copy(),
            certainty=self._certainty
        )
    def get_position(self):
        return self._current_position
    def _create_next_pointer(self, context: TextRecognizeContext, node: NormalizedNode) -> Self:
        if context.is_failed():
            return None
        new_position = context.index()
        certainty = context.last_certainty()
        if certainty <= 1e-8:
            return None
        if certainty > 100:
            certainty = 100

        new_item = HistoryItem(
            node=node,
            prev_point=self._current_position,
            included=context.get_consumed(),
            result=context.get_result(),
            next_point=new_position
        )
        return RecPointer(
            at_state=self._at_state,
            of_data=self._of_data,
            current_position=new_position,
            history=self._history.extend(new_item),
            certainty=certainty
        )

    def advance_with_analyzer(self, node : NormalizedNode, analyzer: GenericContextAnalyzer) -> List[Self]:
        result_pointers: List[RecPointer] = []
        def _on_interrupt(ctx: TextRecognizeContext):

            next_pointer = self._create_next_pointer(ctx, node)
            if next_pointer is not None:
                result_pointers.append(next_pointer)

        node_type = 'automatic'
        if node.node_type == HistoryNodeType.WORD:
            node_type = 'word'
        elif node.node_type == HistoryNodeType.MATCHING:
            node_type = 'matching'

        shared_node = SharedNode(
            connection_type=node_type,
            argument=node.argument,
            name=node.name
        )

        context: TextRecognizeContext = self._of_data.create_context(_on_interrupt,
                                                                     self._current_position,
                                                                     stack=self._stack,
                                                                     flags=self._flags,
                                                                     node=shared_node)
        analyzer.process(context)
        _on_interrupt(context)
        return result_pointers

    def is_finished(self):
        return self._at_state.is_final() and self._current_position >= self._of_data.size()

    def is_final(self):
        return self._at_state.is_final()

    def get_history(self) -> NorHistory:
        return self._history

    def flags(self):
        return self._flags