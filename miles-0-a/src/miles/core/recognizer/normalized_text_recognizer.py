import re
from random import shuffle
from typing import List, Self

from src.miles.core.normalized.history import NorHistory, HistoryItem
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher, NormalizedConnection, NodeType, \
    NormalizedState, NormalizedNode
from src.miles.core.recognizer.context_analyzer import AutomaticContextAnalyzer, WordContextAnalyzer, \
    GenericContextAnalyzer
from src.miles.core.recognizer.generic_recognizer import Recognizer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.optimization import TextOptimizationStrategy
from src.miles.core.recognizer.recognize_context import RecognizeContext
from src.miles.utils.decorators import auto_str
from src.miles.utils.strings import print_list


class _TokenCollection:
    def __init__(self, arr: List[str]):
        self._tokens = arr

    def __len__(self):
        return len(self._tokens)

    def __str__(self):
        return print_list(self._tokens)

    def tokens(self) -> List[str]:
        return list(self._tokens)

    def size(self):
        return len(self._tokens)

class _Pointer:

    _history: NorHistory
    _token_collection: _TokenCollection

    def __init__(self,
                 at_state: NormalizedState,
                 tokens: _TokenCollection,
                 current_position = 0,
                 history: NorHistory | None = None):
        self._at_state = at_state
        self._token_collection = tokens
        self._current_position = current_position

        if history is None:
            history = NorHistory()
        self._history = history

    def __eq__(self, other):
        if not isinstance(other, _Pointer):
            return False
        return self._at_state == other._at_state and self._history == other._history

    def __str__(self):
        return f"Pointer {self._at_state}"

    def get_state(self) -> NormalizedState:
        return self._at_state

    def move_to(self, state: NormalizedState) -> Self:
        return _Pointer(
            at_state=state,
            tokens=self._token_collection,
            current_position=self._current_position,
            history=self._history
        )

    def _create_next_pointer(self, context: RecognizeContext, node: NormalizedNode) -> Self:
        new_position = context.index()

        new_item = HistoryItem(
            node=node,
            prev_point=self._current_position,
            included=context.get_consumed(),
            next_point=new_position
        )
        return _Pointer(
            at_state=self._at_state,
            tokens=self._token_collection,
            current_position=new_position,
            history=self._history.extend(new_item)
        )

    def advance_with_analyzer(self, node : NormalizedNode, analyzer: GenericContextAnalyzer) -> List[Self]:

        result_pointers: List[_Pointer] = []
        def _on_interrupt(ctx: RecognizeContext):
            if ctx.is_failed():
                return
            next_pointer = self._create_next_pointer(ctx, node)
            if next_pointer is not None:
                result_pointers.append(next_pointer)

        context = RecognizeContext(self._token_collection.tokens(), _on_interrupt, start_at=self._current_position)
        analyzer.process(context)
        _on_interrupt(context)
        return result_pointers

    def is_finished(self):
        return self._at_state.is_final() and self._current_position >= self._token_collection.size()

    def get_history(self) -> NorHistory:
        return self._history

class MatchingResult:
    def __init__(self, move: bool = False, append: bool = False, destroy: bool = False):
        self.move = move
        self.append = append
        self.destroy = destroy
    def __str__(self):
        s = '{ '
        if self.move:
            s += 'MOVE '
        if self.append:
            s += 'APPEND '
        if self.destroy:
            s += 'DESTROY '
        s += '}'
        return s

@auto_str
class _TRReader:
    _pointers: List[_Pointer]
    _reached_pointer: _Pointer | None

    def __init__(self,
                 matcher: NormalizedMatcher,
                 text: str,
                 definitions: MatchingDefinitionSet | None = None):
        self._matcher = matcher
        self._text = text
        self._pointers = []
        self._reached_pointer = None

        if definitions is None:
            definitions = MatchingDefinitionSet()
        self._definitions = definitions

    def recognize(self):
        self._pointers = []
        self._reached_pointer = None
        self._recognize_tokens()
        return self._reached_pointer

    def _create_token_collection(self) -> _TokenCollection:
        arr = re.split(r'\s+', self._text.strip()) if self._text.strip() else []
        return _TokenCollection(arr)

    def _recognize_tokens(self):
        initial = self._matcher.initial_state()
        first_pointer = _Pointer(initial, self._create_token_collection())
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _run_token_recognition_loop(self):
        while len(self._pointers) > 0 and self._reached_pointer is None:
            first = self._pointers.pop(0)
            advanced = self._advance_pointer(first)
            self._add_to_pointers(advanced)

    def _add_to_pointers(self, new_pointers: List[_Pointer]):
        new_items: List[_Pointer] = []
        for p in new_pointers:
            add = True
            for r in self._pointers:
                if p == r:
                    add = False
                    break
            if add:
                new_items.append(p)
        self._pointers[:0] = new_items

    def _advance_pointer(self, pointer: _Pointer) -> List[_Pointer]:
        if pointer.is_finished():
            self._reached_pointer = pointer
            return []

        state = pointer.get_state()
        next_gen_pointers: List[_Pointer] = []
        ordered_connection = self._all_connections_ordered(state)
        for connection in ordered_connection:
            self._go_through_connection(pointer, connection)

        return next_gen_pointers

    def _go_through_connection(self, pointer: _Pointer, connection: NormalizedConnection) -> List[_Pointer]:
        nodes = connection.get_nodes()
        previous_generation = [ pointer ]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                if node.node_type == NodeType.AUTOMATIC:
                    analyzer = AutomaticContextAnalyzer()
                    advance = p.advance_with_analyzer(node, analyzer)
                    advance = self._optimized_route(advance, analyzer)
                    this_generation.extend(advance)

                elif node.node_type == NodeType.WORD:
                    word = node.argument
                    analyzer = WordContextAnalyzer(word)
                    advance = p.advance_with_analyzer(node, analyzer)
                    advance = self._optimized_route(advance, analyzer)
                    this_generation.extend(advance)

                elif node.node_type == NodeType.MATCHING:
                    name = node.argument
                    analyzer = self._definitions.get_matching(name).analyzer()
                    advance = p.advance_with_analyzer(node, analyzer)
                    advance = self._optimized_route(advance, analyzer)
                    this_generation.extend(advance)
                else:
                    raise ValueError(f'Unknown node type {node.node_type.name}')
            previous_generation = this_generation

        return previous_generation

    def _all_connections_ordered(self, state: NormalizedState) -> List[NormalizedConnection]:
        lst = state.all_connections()
        return sorted(lst, key=lambda c: state.get_priority(c), reverse=True)


    def _optimized_route(self, next_gen_pointers: List[_Pointer], analyzer: GenericContextAnalyzer) -> List[_Pointer]:
        lst = list(next_gen_pointers)
        optimization_strategy = analyzer.optimization_strategy()
        if optimization_strategy == TextOptimizationStrategy.NONE or optimization_strategy is None:
            return lst
        elif optimization_strategy == TextOptimizationStrategy.SHORTEST_FIRST:
            return sorted(lst, key=lambda p: p.get_history().last().step())
        elif optimization_strategy == TextOptimizationStrategy.LONGEST_FIRST:
            return sorted(lst, key=lambda p: p.get_history().last().step(), reverse=True)
        elif optimization_strategy == TextOptimizationStrategy.RANDOMIZE:
            shuffle(lst)
            return lst
        else:
            raise ValueError(f'Unexpected optimization strategy: {optimization_strategy.name}')



class TextRecognizer(Recognizer):
    _pointers: List[_Pointer]
    _reached_pointers: List[_Pointer]
    __token_stream : None | _TokenCollection
    def __init__(self, matcher: NormalizedMatcher, text: str, definitions: MatchingDefinitionSet):
        self._reader = _TRReader(matcher, text, definitions)

    def recognize(self):
        reached_pointers = self._reader.recognize()