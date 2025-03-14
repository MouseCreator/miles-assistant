import re
from typing import List, Self, Set

from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType, MatchConnection
from src.miles.core.recognizer.context_analyzer import WordContextAnalyzer, GenericContextAnalyzer
from src.miles.core.recognizer.generic_recognizer import Recognizer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.recognize_context import RecognizeContext


class _HistoryItem:
    def __init__(self,
                 prev_state: MatchState,
                 connection: MatchConnection,
                 token: str,
                 label: str):
        self.prev_state = prev_state
        self.connection = connection
        self.token = token
        self.label = label

    def __eq__(self, other):
        if not isinstance(other, _HistoryItem):
            return False
        return (
                self.prev_state == other.prev_state
                and self.connection == other.connection
                and self.token == other.token
                and self.label == other.label
                )

class _Pointer:

    _history: List[_HistoryItem]
    _context: RecognizeContext

    def __init__(self,
                 at_state: MatchState,
                 context: RecognizeContext,
                 history: List[_HistoryItem] | None = None):
        self._at_state = at_state
        self._context = context
        if history is None:
            self._history = []
        else:
            self._history = list(history)

    def __eq__(self, other):
        if not isinstance(other, _Pointer):
            return False
        return self._at_state == other._at_state and self._history == other._history
    def __str__(self):
        return f"Pointer {self._at_state}"

    def get_state(self) -> MatchState:
        return self._at_state

    def advance_with_analyzer(self, connection : MatchConnection, analyzer: GenericContextAnalyzer) -> Self | None:
        index_before = self._context.index()
        analyzer.process(self._context)
        index_after = self._context.index()
        if self._context.is_failed():
            return None
        return self._move_to() ### ###

    def auto_advance(self, connection: MatchConnection) -> List[Self]:
        return []

    def is_finished(self):
        return self._at_state.is_final() and self._context.is_empty()


class _RecTokenStream:
    def __init__(self, arr: List[str]):
        self._tokens = arr
        self.current = -1
    def next_token(self) -> str:
        self.current += 1
        return self._tokens[self.current]
    def has_tokens(self) -> bool:
        return self.current + 1 < len(self._tokens)

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


class _TRReader:
    _pointers: List[_Pointer]
    _reached_pointers: List[_Pointer]
    __token_stream: None | _RecTokenStream

    def __init__(self, matcher: Matcher, text: str, definitions: MatchingDefinitionSet):
        self._matcher = matcher
        self._text = text
        self._token_stream = None
        self._pointers = []
        self._reached_pointers = []
        self._definitions = definitions

    def recognize(self):
        self._pointers = []
        self._reached_pointers = []
        self._create_token_stream()
        self._recognize_tokens()
        return list(self._reached_pointers)

    def _create_token_stream(self):
        arr = re.split(r'\s+', self._text)
        self._token_stream = _RecTokenStream(arr)

    def _recognize_tokens(self):
        initial = self._matcher.get_initial_state()
        arr = re.split(r'\s+', self._text)
        context = RecognizeContext(arr)
        first_pointer = _Pointer(initial, context)
        self._pointers.append(first_pointer)

        self._run_token_recognition_loop()

        for pointer in self._pointers:
            if pointer.get_state().is_final():
                # keep only the pointers that reached a FINAL state after all tokens were consumed
                self._reached_pointers.append(pointer)

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
        while True:
            for p in self._pointers:
                self._advance_pointer(p)

    def _advance_pointer(self, p: _Pointer) -> List[_Pointer]:

        if p.is_finished():
            self._reached_pointers.append(p)
            return []

        state = p.get_state()
        next_gen_pointers: List[_Pointer] = []
        for connection in state.all_connections():
            if connection.connection_type == ConnectionType.AUTOMATIC:
                advances = p.auto_advance(connection)
                next_gen_pointers.extend(advances)

            elif connection.connection_type == ConnectionType.MATCHING:
                word = connection.connection_arg
                analyzer = WordContextAnalyzer(word)
                advance = p.advance_with_analyzer(connection, analyzer)
                if advance is not None:
                    next_gen_pointers.append(advance)
            elif connection.connection_type == ConnectionType.WORD:
                plugin = connection.plugin
                name = connection.connection_arg
                analyzer = self._definitions.get_matching(plugin, name).analyzer()
                advance = p.advance_with_analyzer(connection, analyzer)
                if advance is not None:
                    next_gen_pointers.append(advance)
            else:
                raise ValueError(f'Unknown connection type {connection.connection_type.name}')
        return next_gen_pointers


class TextRecognizer(Recognizer):
    _pointers: List[_Pointer]
    _reached_pointers: List[_Pointer]
    __token_stream : None | _RecTokenStream
    def __init__(self, matcher: Matcher, text: str, definitions: MatchingDefinitionSet):
        self._reader = _TRReader(matcher, text, definitions)

    def recognize(self):
        reached_pointers = self._reader.recognize()







