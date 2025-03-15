import re
from random import shuffle
from typing import List, Self, Set, Tuple

from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType, MatchConnection
from src.miles.core.recognizer.context_analyzer import WordContextAnalyzer, GenericContextAnalyzer, \
    AutomaticContextAnalyzer
from src.miles.core.recognizer.generic_recognizer import Recognizer
from src.miles.core.recognizer.history import HistoryItem, RecHistory
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.optimization import TextOptimizationStrategy
from src.miles.core.recognizer.priority import PriorityManager
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

class _VisitedStates:
    def __init__(self, states: None | Set[Tuple[MatchState, int]] = None):
        if states is None:
            states = set()
        self._states = set(states)

    def extend(self, state: MatchState, position: int) -> Self:
        return _VisitedStates( self._states | {(state, position)} )

    def is_visited(self, state: MatchState, position: int):
        pair = (state, position)
        return pair in self._states

class _Pointer:

    _history: RecHistory
    _token_collection: _TokenCollection
    _visited: _VisitedStates

    def __init__(self,
                 at_state: MatchState,
                 tokens: _TokenCollection,
                 current_position = 0,
                 history: RecHistory | None = None,
                 visited: _VisitedStates | None = None):
        self._at_state = at_state
        self._visited = visited
        self._token_collection = tokens
        self._current_position = current_position

        if history is None:
            history = RecHistory()
        self._history = history

        if visited is None:
            visited = _VisitedStates()
        self._visited = visited

    def __eq__(self, other):
        if not isinstance(other, _Pointer):
            return False
        return self._at_state == other._at_state and self._history == other._history

    def __str__(self):
        return f"Pointer {self._at_state}"

    def get_state(self) -> MatchState:
        return self._at_state

    def _create_next_pointer(self, context: RecognizeContext, connection: MatchConnection) -> Self:
        new_position = context.index()
        destination = self._at_state.get_destination(connection)

        if self._visited.is_visited(destination, new_position):
            return None

        new_item = HistoryItem(
            prev_state=self._at_state,
            connection=connection,
            prev_point=self._current_position,
            included=context.get_consumed(),
            next_point=new_position
        )
        return _Pointer(
            at_state=destination,
            tokens=self._token_collection,
            current_position=new_position,
            history=self._history.extend(new_item),
            visited=self._visited.extend(destination, new_position)
        )


    def advance_with_analyzer(self, connection : MatchConnection, analyzer: GenericContextAnalyzer) -> List[Self]:

        result_pointers: List[_Pointer] = []

        def _on_interrupt(ctx: RecognizeContext):
            if ctx.is_failed():
                return
            next_pointer = self._create_next_pointer(ctx, connection)
            if next_pointer is not None:
                result_pointers.append(next_pointer)

        context = RecognizeContext(self._token_collection.tokens(), _on_interrupt, start_at=self._current_position)
        analyzer.process(context)
        _on_interrupt(context)
        return result_pointers

    def is_finished(self):
        return self._at_state.is_final() and self._current_position >= self._token_collection.size()

    def get_history(self) -> RecHistory:
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
                 matcher: Matcher,
                 text: str,
                 definitions: MatchingDefinitionSet | None = None,
                 priority_manager: PriorityManager | None = None):
        self._matcher = matcher
        self._text = text
        self._pointers = []
        self._reached_pointer = None

        if definitions is None:
            definitions = MatchingDefinitionSet()
        self._definitions = definitions

        if priority_manager is None:
            priority_manager = PriorityManager()
        self._priority_manager = priority_manager

    def recognize(self):
        self._pointers = []
        self._reached_pointer = None
        self._recognize_tokens()
        return self._reached_pointer

    def _create_token_collection(self) -> _TokenCollection:
        arr = re.split(r'\s+', self._text.strip()) if self._text.strip() else []
        return _TokenCollection(arr)

    def _recognize_tokens(self):
        initial = self._matcher.get_initial_state()
        first_pointer = _Pointer(initial, self._create_token_collection())
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

    def _fill_automatic_paths(self):
        visited_states: Set[MatchState] = set()
        active_pointers = list(self._pointers)
        new_pointers = list(self._pointers)
        while len(active_pointers) > 0:
            p = active_pointers.pop(0)
            state = p.get_state()
            if state in visited_states:
                continue
            for conn in state.all_connections():
                if conn.connection_type == ConnectionType.AUTOMATIC:
                    destination = state.get_destination(conn)
                    if destination not in visited_states:
                        p_n = p.move_to(conn, destination, None)
                        active_pointers.append(p_n)
                        new_pointers.append(p_n)
        self._pointers = new_pointers

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

    def _advance_pointer(self, p: _Pointer) -> List[_Pointer]:
        print(p)
        if p.is_finished():
            self._reached_pointer = p
            return []

        state = p.get_state()
        next_gen_pointers: List[_Pointer] = []
        ordered_connection = self._all_connections_ordered(state.all_connections())
        for connection in ordered_connection:
            if connection.connection_type == ConnectionType.AUTOMATIC:
                analyzer = AutomaticContextAnalyzer()
                advance = p.advance_with_analyzer(connection, analyzer)
                advance = self._optimized_route(advance, analyzer)
                next_gen_pointers.extend(advance)

            elif connection.connection_type == ConnectionType.WORD:
                word = connection.connection_arg
                analyzer = WordContextAnalyzer(word)
                advance = p.advance_with_analyzer(connection, analyzer)
                advance = self._optimized_route(advance, analyzer)
                next_gen_pointers.extend(advance)

            elif connection.connection_type == ConnectionType.MATCHING:
                plugin = connection.plugin
                name = connection.connection_arg
                analyzer = self._definitions.get_matching(plugin, name).analyzer()
                advance = p.advance_with_analyzer(connection, analyzer)
                advance = self._optimized_route(advance, analyzer)
                next_gen_pointers.extend(advance)

            else:
                raise ValueError(f'Unknown connection type {connection.connection_type.name}')
        return next_gen_pointers

    def _all_connections_ordered(self, connection_arr: List[MatchConnection]) -> List[MatchConnection]:
        lst = list(connection_arr)
        return sorted(lst, key=lambda c: self._priority_manager.get_priority(c), reverse=True)


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
    def __init__(self, matcher: Matcher, text: str, definitions: MatchingDefinitionSet):
        self._reader = _TRReader(matcher, text, definitions)

    def recognize(self):
        reached_pointers = self._reader.recognize()







