
from random import shuffle
from typing import List, Set, Tuple

from src.miles.core.context.data_holder import TextDataHolder
from src.miles.core.plugin.plugin_structure import NamespaceComponent
from src.miles.core.priority.dynamic_priority import DynamicPriorityRuleSet
from src.miles.core.executor.command_structure import CommandStructure, NamespaceStructure
from src.miles.core.recognizer.analyzer_provider import AnalyzerProvider
from src.miles.core.recognizer.history_to_struct import StructFactory
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher, NormalizedConnection
from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer
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

    def clear(self):
        self._cache = set()


@auto_str
class _CommandReader:
    _pointers: List[RecPointer]
    _reached_pointer: RecPointer | None
    _analyzers: AnalyzerProvider
    _cache: _DynamicCache
    _dynamic_priorities: DynamicPriorityRuleSet

    def __init__(self,
                 matcher: NormalizedMatcher,
                 input_data: TextDataHolder,
                 start_from: int,
                 analyzer_provider: AnalyzerProvider,
                 dynamic_priorities: DynamicPriorityRuleSet | None):
        self._matcher = matcher
        self._input_data = input_data
        self._pointers = []
        self._reached_pointer = None
        self._start_from = start_from
        self._cache = _DynamicCache()

        if analyzer_provider is None:
            analyzer_provider = MatchingDefinitionSet()
        self._analyzers = analyzer_provider

        if dynamic_priorities is None:
            dynamic_priorities = DynamicPriorityRuleSet()
        self._dynamic_priorities = dynamic_priorities

    def recognize(self):
        self._pointers = []
        self._reached_pointer = None
        self._cache.clear()
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


        next_gen_pointers: List[RecPointer] = []
        ordered_connections = self._all_connections_ordered(pointer)
        for connection in ordered_connections:
            new_pointers = self._go_through_connection(pointer, connection)
            next_gen_pointers.extend(new_pointers)

        return next_gen_pointers

    def _go_through_connection(self, pointer: RecPointer, connection: NormalizedConnection) -> List[RecPointer]:
        nodes = connection.get_nodes()
        previous_generation = [ pointer ]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                analyzer = self._analyzers.provide_analyzer(node.node_type, node.argument)
                advance = p.advance_with_analyzer(node, analyzer)
                advance = self._optimized_route(advance, analyzer)
                this_generation.extend(advance)
            previous_generation = this_generation

        return previous_generation

    def _all_connections_ordered(self, pointer: RecPointer) -> List[NormalizedConnection]:
        state = pointer.get_state()
        connections_from_state = state.all_connections()

        priority_map = {}
        for c in connections_from_state:
            priority = state.get_priority(c)
            connection_origin = c.get_nodes()[0]
            for d in self._dynamic_priorities.get_rules():
                context = self._input_data.dynamic_priority_context(
                    start_at=pointer.get_position(),
                    flags=pointer.flags(),
                    connection_type=connection_origin.node_type,
                    connection_arg=connection_origin.argument,
                    connection_name=connection_origin.name,
                    priority=priority
                )
                if d.is_applicable(context):
                    priority = d.priority(context)
            priority_map[c] = priority

        return sorted(connections_from_state, key=lambda x: priority_map[x], reverse=True)

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
@auto_str
class _NamespaceReader:
    _pointers: List[RecPointer]
    _reached_pointer: RecPointer | None
    _cache: _DynamicCache

    def __init__(self,
                 matcher: NormalizedMatcher,
                 input_data: TextDataHolder):
        self._matcher = matcher
        self._input_data = input_data
        self._pointers = []
        self._reached_pointer = None
        self._previous_reached = None
        self._cache = _DynamicCache()

    def recognize(self):
        self._pointers = []
        self._reached_pointer = None
        self._previous_reached = None
        self._cache.clear()
        self._recognize_tokens()

        return self._reached_pointer

    def _recognize_tokens(self):
        initial = self._matcher.initial_state()
        first_pointer = RecPointer(initial, self._input_data)
        self._cache.add_to_cache(first_pointer)
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _run_token_recognition_loop(self):
        while self._reached_pointer is None:
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
        if pointer.is_final():
            self._previous_reached = pointer

        next_gen_pointers: List[RecPointer] = []
        ordered_connections = self._all_connections_ordered(pointer)
        for connection in ordered_connections:
            new_pointers = self._go_through_connection(pointer, connection)
            next_gen_pointers.extend(new_pointers)

        return next_gen_pointers

    def _go_through_connection(self, pointer: RecPointer, connection: NormalizedConnection) -> List[RecPointer]:
        nodes = connection.get_nodes()
        previous_generation = [pointer]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                analyzer = self._analyzers.provide_analyzer(node.node_type, node.argument)
                advance = p.advance_with_analyzer(node, analyzer)
                advance = self._optimized_route(advance, analyzer)
                this_generation.extend(advance)
            previous_generation = this_generation

        return previous_generation

def recognize_namespace(matcher: NormalizedMatcher, tokens: List[str]) -> NamespaceStructure:
    of_data = TextDataHolder(tokens)
    recognizer = _CommandReader(matcher, of_data, 0, AnalyzerProvider(MatchingDefinitionSet()), None)
    pointer: RecPointer = recognizer.recognize()
    struct_factory = StructFactory()
    return struct_factory.convert_namespace(tokens, pointer)

def recognize_command(nc: NamespaceComponent, tokens: List[str], ns: NamespaceStructure) -> CommandStructure:
    of_data = TextDataHolder(tokens)
    shift = ns.size()
    matcher = nc.command_matcher
    dynamic_priorities = nc.dynamic_priorities
    analyzer_provider = AnalyzerProvider(nc.definitions)
    recognizer = _CommandReader(matcher, of_data, shift, analyzer_provider, dynamic_priorities)
    pointer: RecPointer = recognizer.recognize()
    struct_factory = StructFactory()
    return struct_factory.convert_command(ns, tokens, pointer)