
from random import shuffle
from typing import List, Set, Tuple

from src.miles.core.context.data_holder import InputDataHolder
from src.miles.core.recognizer.analyzer_provider import AnalyzerProvider
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher, NormalizedConnection, NormalizedState
from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer
from src.miles.core.recognizer.generic_recognizer import Recognizer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.optimization import RecOptimizationStrategy
from src.miles.core.recognizer.recognizer_pointer import RecPointer
from src.miles.utils.decorators import auto_str


class _DynamicCache:
    _cache: Set[Tuple[int, int]]
    def __init__(self):
        self._cache = set()

    def _pair(self, pointer: RecPointer):
        state_id = pointer.get_state().get_id()
        position = pointer.get_position()
        return (state_id, position)

    def add_to_cache(self, pointer: RecPointer):

        self._cache.add(self._pair(pointer))
    def is_in_cache(self, pointer: RecPointer):
        return self._pair(pointer) in self._cache

    def __contains__(self, item):
        if not isinstance(item, RecPointer):
            return False
        return self.is_in_cache(item)

@auto_str
class _TRReader:
    _pointers: List[RecPointer]
    _reached_pointer: RecPointer | None
    _analyzers: AnalyzerProvider
    _cache: _DynamicCache

    def __init__(self,
                 matcher: NormalizedMatcher,
                 input_data: InputDataHolder,
                 start_from: int,
                 analyzer_provider: AnalyzerProvider):
        self._matcher = matcher
        self._input_data = input_data
        self._pointers = []
        self._dynamic_cache = _DynamicCache
        self._reached_pointer = None
        self._start_from = start_from

        if analyzer_provider is None:
            analyzer_provider = MatchingDefinitionSet()
        self._analyzers = analyzer_provider

    def recognize(self):
        self._pointers = []
        self._reached_pointer = None
        self._recognize_tokens()
        return self._reached_pointer

    def _recognize_tokens(self):
        initial = self._matcher.initial_state()
        first_pointer = RecPointer(initial, self._input_data, current_position=self._start_from)
        self._cache.add_to_cache(first_pointer)
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _run_token_recognition_loop(self):
        while len(self._pointers) > 0 and self._reached_pointer is None:
            first = self._pointers.pop(0)
            advanced = self._advance_pointer(first)
            self._add_to_pointers(advanced)

    def _add_to_pointers(self, new_pointers: List[RecPointer]):
        new_items: List[RecPointer] = []
        for p in new_pointers:
            if p not in self._cache:
                new_items.append(p)

        for item in new_items:
            self._cache.add_to_cache(item)

        self._pointers[:0] = new_items

    def _advance_pointer(self, pointer: RecPointer) -> List[RecPointer]:
        if pointer.is_finished():
            self._reached_pointer = pointer
            return []

        state = pointer.get_state()
        next_gen_pointers: List[RecPointer] = []
        ordered_connection = self._all_connections_ordered(state)
        for connection in ordered_connection:
            self._go_through_connection(pointer, connection)

        return next_gen_pointers

    def _go_through_connection(self, pointer: RecPointer, connection: NormalizedConnection) -> List[RecPointer]:
        nodes = connection.get_nodes()
        previous_generation = [ pointer ]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                analyzer = self._analyzers.provide_analyzer(self._input_data.type(),
                                                            node.node_type,
                                                            node.argument)
                advance = p.advance_with_analyzer(node, analyzer)
                advance = self._optimized_route(advance, analyzer)
                this_generation.extend(advance)
            previous_generation = this_generation

        return previous_generation

    def _all_connections_ordered(self, state: NormalizedState) -> List[NormalizedConnection]:
        lst = state.all_connections()
        return sorted(lst, key=lambda c: state.get_priority(c), reverse=True)

    def _optimized_route(self, next_gen_pointers: List[RecPointer], analyzer: GenericContextAnalyzer) -> List[RecPointer]:
        lst = list(next_gen_pointers)
        optimization_strategy = analyzer.optimization_strategy()
        if optimization_strategy == RecOptimizationStrategy.NONE or optimization_strategy is None:
            return lst
        elif optimization_strategy == RecOptimizationStrategy.SHORTEST_FIRST:
            return sorted(lst, key=lambda p: p.get_history().last().step())
        elif optimization_strategy == RecOptimizationStrategy.LONGEST_FIRST:
            return sorted(lst, key=lambda p: p.get_history().last().step(), reverse=True)
        elif optimization_strategy == RecOptimizationStrategy.RANDOMIZE:
            shuffle(lst)
            return lst
        else:
            raise ValueError(f'Unexpected optimization strategy: {optimization_strategy.name}')



class TextRecognizer(Recognizer):
    _pointers: List[RecPointer]
    _reached_pointers: List[RecPointer]
    def __init__(self, matcher: NormalizedMatcher, of_data: InputDataHolder, provider: AnalyzerProvider, start_from: int):
        self._reader = _TRReader(matcher, of_data, start_from, provider)

    def recognize(self):
        reached_pointers = self._reader.recognize()