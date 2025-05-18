from random import shuffle
from typing import List, Set, Tuple

from src.miles.core.plugin.plugin_structure import NamespaceComponent
from src.miles.core.recognizer.analyzer_provider import AnalyzerProvider
from src.miles.core.recognizer.history_to_struct import StructFactory
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher, NormalizedConnection
from src.miles.core.recognizer.optimization import RecOptimizationStrategy
from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.core.recognizer.recognizer_pointer import RecPointer
from src.miles.core.recognizer.recognizer_stack import RecognizerStack
from src.miles.shared.certainty import CertaintyDecision, CertaintyItem, CertaintyEffect
from src.miles.shared.context.data_holder import TextDataHolder
from src.miles.shared.context.flags import Flags
from src.miles.shared.context_analyzer import GenericContextAnalyzer, DefaultWordContextAnalyzerFactory
from src.miles.shared.executor.command_structure import NamespaceStructure, CommandStructure
from src.miles.shared.priority.dynamic_priority import DynamicPriorityRuleSet
from src.miles.utils.decorators import auto_str


def _optimized_route(next_gen_pointers: List[RecPointer], analyzer: GenericContextAnalyzer) -> List[RecPointer]:
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


class _DynamicCache:
    _cache: Set[Tuple[int, int]]

    def __init__(self):
        self._cache = set()

    def _pair(self, pointer: RecPointer):
        state_id = pointer.get_state().get_id()
        position = pointer.get_position()
        return state_id, position

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
class _ExtendedCommandReader:
    _pointers: List[RecPointer]
    _reached_pointers: List[RecPointer]
    _failed_max_pointer: RecPointer | None
    _analyzers: AnalyzerProvider
    _cache: _DynamicCache
    _dynamic_priorities: DynamicPriorityRuleSet
    _certainty_effect: CertaintyEffect

    def __init__(self,
                 matcher: NormalizedMatcher,
                 input_data: TextDataHolder,
                 start_from: int,
                 analyzer_provider: AnalyzerProvider,
                 dynamic_priorities: DynamicPriorityRuleSet | None,
                 certainty_effect: CertaintyEffect,
                 stack: RecognizerStack,
                 flags: Flags):
        self._matcher = matcher
        self._input_data = input_data
        self._certainty_effect = certainty_effect
        self._pointers = []
        self._reached_pointers = []
        self._failed_max_pointer = None
        self._start_from = start_from
        self._cache = _DynamicCache()
        self._initial_stack = stack
        self._initial_flags = flags

        if analyzer_provider is None:
            analyzer_provider = MatchingDefinitionSet()
        self._analyzers = analyzer_provider

        if dynamic_priorities is None:
            dynamic_priorities = DynamicPriorityRuleSet()
        self._dynamic_priorities = dynamic_priorities

    def recognize(self):
        self._pointers = []
        self._reached_pointers = []
        self._cache.clear()
        self._failed_max_pointer = None
        self._recognize_tokens()
        result = list(self._reached_pointers)
        return sorted(result, key=lambda p: p.get_position(), reverse=True)

    def _recognize_tokens(self):
        initial = self._matcher.initial_state()
        first_pointer = RecPointer(initial,
                                   self._input_data,
                                   current_position=self._start_from,
                                   flags=self._initial_flags,
                                   stack=self._initial_stack)
        self._failed_max_pointer = first_pointer
        self._cache.add_to_cache(first_pointer)
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _run_token_recognition_loop(self):
        while len(self._pointers) > 0:
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
            self._reached_pointers.append(pointer)

        next_gen_pointers: List[RecPointer] = []
        ordered_connections = self._all_connections_ordered(pointer)
        pointers_count = 0
        pointers_dict = {}
        decision = CertaintyDecision()
        category_count = 0
        for connection in ordered_connections:
            new_pointers = self._go_through_connection(pointer, connection)

            if len(new_pointers) > 0:
                category_count += 1
                items = []
                for np in new_pointers:
                    pointers_count += 1
                    pointers_dict[pointers_count] = np
                    item = CertaintyItem(pointers_count, category_count, np.certainty(), np.flags().copy())
                    items.append(item)
                decision.add(items)
                next_gen_pointers.extend(new_pointers)

        target_order = self._certainty_effect.apply(decision)
        result = []
        for item in target_order:
            pointer = pointers_dict[item.identity]
            result.append(pointer)

        return result

    def _go_through_connection(self, pointer: RecPointer, connection: NormalizedConnection) -> List[RecPointer]:
        nodes = connection.get_nodes()
        previous_generation = [pointer]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                analyzer = self._analyzers.provide_analyzer(node.node_type, node.argument)
                advance = p.advance_with_analyzer(node, analyzer)
                advance = _optimized_route(advance, analyzer)

                if len(advance) == 0:  # failed pointer
                    position = p.get_position()
                    prev_max = self._failed_max_pointer.get_position()
                    if position > prev_max:
                        self._failed_max_pointer = p

                this_generation.extend(advance)
            previous_generation = this_generation

        destination = pointer.get_state().get_destination(connection)
        result = []
        for p in previous_generation:
            r = p.move_to(destination)
            result.append(r)
        return result

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


@auto_str
class _CommandReader:
    _pointers: List[RecPointer]
    _reached_pointer: RecPointer | None
    _failed_max_pointer: RecPointer | None
    _analyzers: AnalyzerProvider
    _cache: _DynamicCache
    _certainty_effect: CertaintyEffect
    _dynamic_priorities: DynamicPriorityRuleSet

    def __init__(self,
                 matcher: NormalizedMatcher,
                 input_data: TextDataHolder,
                 start_from: int,
                 analyzer_provider: AnalyzerProvider,
                 certainty_effect: CertaintyEffect,
                 dynamic_priorities: DynamicPriorityRuleSet | None,
                 flags: Flags):
        self._matcher = matcher
        self._input_data = input_data
        self._pointers = []
        self._certainty_effect = certainty_effect
        self._reached_pointer = None
        self._failed_max_pointer = None
        self._start_from = start_from
        self._cache = _DynamicCache()
        if flags is None:
            flags = Flags()
        self._initial_flags = flags
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
        self._failed_max_pointer = None
        self._recognize_tokens()
        return self._reached_pointer

    def _recognize_tokens(self):
        initial = self._matcher.initial_state()
        first_pointer = RecPointer(initial,
                                   self._input_data,
                                   current_position=self._start_from,
                                   flags=self._initial_flags.copy())
        self._failed_max_pointer = first_pointer
        self._cache.add_to_cache(first_pointer)
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _run_token_recognition_loop(self):
        while len(self._pointers) > 0 and self._reached_pointer is None:
            first = self._pointers.pop(0)
            advanced = self._advance_pointer(first)
            self._add_to_pointers(advanced)

        if self._reached_pointer is None:
            position = self._failed_max_pointer.get_position()
            if position < self._input_data.size():
                error_token = self._input_data[position]
                message = f'Unable to recognize command! Error at position {position + 1}: {error_token}'
                raise RecognizerError(message)
            else:
                raise RecognizerError(f'Unable to recognize command! Unexpected end of input.')

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
        pointers_count = 0
        pointers_dict = {}
        decision = CertaintyDecision()
        category_count = 0
        for connection in ordered_connections:
            new_pointers = self._go_through_connection(pointer, connection)

            if len(new_pointers) > 0:
                category_count += 1
                items = []
                for np in new_pointers:
                    pointers_count += 1
                    pointers_dict[pointers_count] = np
                    item = CertaintyItem(pointers_count, category_count, np.certainty(), np.flags().copy())
                    items.append(item)
                decision.add(items)
                next_gen_pointers.extend(new_pointers)

        target_order = self._certainty_effect.apply(decision)
        result = []
        for item in target_order:
            pointer = pointers_dict[item.identity]
            result.append(pointer)

        return result

    def _go_through_connection(self, pointer: RecPointer, connection: NormalizedConnection) -> List[RecPointer]:
        nodes = connection.get_nodes()
        previous_generation = [pointer]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                analyzer = self._analyzers.provide_analyzer(node.node_type, node.argument)
                advance = p.advance_with_analyzer(node, analyzer)
                advance = _optimized_route(advance, analyzer)

                if len(advance) == 0:  # failed pointer
                    position = p.get_position()
                    prev_max = self._failed_max_pointer.get_position()
                    if position > prev_max:
                        self._failed_max_pointer = p

                this_generation.extend(advance)
            previous_generation = this_generation

        destination = pointer.get_state().get_destination(connection)
        result = []
        for p in previous_generation:
            r = p.move_to(destination)
            result.append(r)
        return result

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


@auto_str
class _NamespaceReader:
    _pointers: List[RecPointer]
    _reached_pointer: RecPointer | None
    _cache: _DynamicCache
    _failed_max_pointer: RecPointer | None

    def __init__(self,
                 matcher: NormalizedMatcher,
                 input_data: TextDataHolder,
                 flags: Flags):
        self._matcher = matcher
        self._input_data = input_data
        self._pointers = []
        self._initial_flags = flags
        self._reached_pointer = None
        self._previous_reached = None
        self._cache = _DynamicCache()
        self._failed_max_pointer = None
        self._analyzers = AnalyzerProvider(MatchingDefinitionSet(), DefaultWordContextAnalyzerFactory())

    def recognize(self):
        self._pointers = []
        self._reached_pointer = None
        self._previous_reached = None
        self._failed_max_pointer = None
        self._cache.clear()
        self._recognize_tokens()

        return self._reached_pointer

    def _recognize_tokens(self):
        initial = self._matcher.initial_state()
        first_pointer = RecPointer(initial, self._input_data, flags=self._initial_flags.copy())
        self._failed_max_pointer = first_pointer
        self._cache.add_to_cache(first_pointer)
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _run_token_recognition_loop(self):
        while self._reached_pointer is None:
            if not self._pointers:
                if self._reached_pointer is None:
                    position = self._failed_max_pointer.get_position()
                    if position < self._input_data.size():
                        error_token = self._input_data[position]
                        message = f'Unable to recognize namespace! Error at position {position + 1}: {error_token}'
                    else:
                        message = f'Unable to recognize namespace! Unexpected end of input.'
                    raise RecognizerError(message)
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

        if not next_gen_pointers:
            if self._previous_reached is None:
                position = pointer.get_position()
                prev_max = self._failed_max_pointer.get_position()
                if position > prev_max:
                    self._failed_max_pointer = pointer

            self._reached_pointer = self._previous_reached

        return next_gen_pointers

    def _all_connections_ordered(self, pointer: RecPointer) -> List[NormalizedConnection]:
        state = pointer.get_state()
        connections_from_state = state.all_connections()
        priority_map = {}
        for c in connections_from_state:
            priority = state.get_priority(c)
            priority_map[c] = priority
        return sorted(connections_from_state, key=lambda x: priority_map[x], reverse=True)

    def _go_through_connection(self, pointer: RecPointer, connection: NormalizedConnection) -> List[RecPointer]:
        nodes = connection.get_nodes()
        previous_generation = [pointer]

        for node in nodes:
            this_generation = []
            for p in previous_generation:
                analyzer = self._analyzers.provide_analyzer(node.node_type, node.argument)
                advance = p.advance_with_analyzer(node, analyzer)
                this_generation.extend(advance)
            previous_generation = this_generation
        destination = pointer.get_state().get_destination(connection)

        result = []
        for p in previous_generation:
            r = p.move_to(destination)
            result.append(r)
        return result


def recognize_namespace(matcher: NormalizedMatcher, tokens: List[str],
                        flags: Flags | None = None) -> NamespaceStructure:
    of_data = TextDataHolder(tokens)
    reader = _NamespaceReader(matcher, of_data, flags=flags)
    pointer: RecPointer = reader.recognize()
    struct_factory = StructFactory()
    return struct_factory.convert_namespace(tokens, pointer)


def recognize_command(nc: NamespaceComponent,
                      tokens: List[str],
                      ns: NamespaceStructure,
                      flags: Flags | None = None) -> CommandStructure:
    of_data = TextDataHolder(tokens)
    shift = ns.size()
    matcher = nc.command_matcher
    dynamic_priorities = nc.dynamic_priorities
    analyzer_provider = AnalyzerProvider(nc.definitions, nc.word_analyzer_factory)
    reader = _CommandReader(matcher, of_data, shift, analyzer_provider, nc.certainty_effect, dynamic_priorities,
                            flags=flags)
    pointer: RecPointer = reader.recognize()
    struct_factory = StructFactory()
    return struct_factory.convert_command(ns, tokens, pointer)


def recognize_extended(title: str,
                       tokens: List[str],
                       nc: NamespaceComponent,
                       start_from: int,
                       stack: RecognizerStack,
                       flags: Flags) -> List[CommandStructure]:
    of_data = TextDataHolder(tokens)
    matcher = nc.command_matcher
    dynamic_priorities = nc.dynamic_priorities
    certainty_effect = nc.certainty_effect
    analyzer_provider = AnalyzerProvider(nc.definitions, nc.word_analyzer_factory)
    reader = _ExtendedCommandReader(matcher, of_data, start_from, analyzer_provider, dynamic_priorities,
                                    certainty_effect, stack, flags)
    pointers: List[RecPointer] = reader.recognize()
    ns = NamespaceStructure(identifier=title, tokens=[])
    struct_factory = StructFactory()

    result = []
    for p in pointers:
        token_subset = tokens[start_from: p.get_position()]
        struct = struct_factory.convert_command(ns, token_subset, p)
        result.append(struct)

    return result
