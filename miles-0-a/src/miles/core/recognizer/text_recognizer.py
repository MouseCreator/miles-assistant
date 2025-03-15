import re
from typing import List, Self, Set

from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType, MatchConnection
from src.miles.core.recognizer.context_analyzer import WordContextAnalyzer, GenericContextAnalyzer
from src.miles.core.recognizer.generic_recognizer import Recognizer
from src.miles.core.recognizer.history import HistoryItem, RecHistory
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.recognize_context import RecognizeContext

class _TokenCollection:
    def __init__(self, arr: List[str]):
        self._tokens = arr
        self.current = -1

    def __len__(self):
        return len(self._tokens)

    def tokens(self) -> List[str]:
        return list(self._tokens)

    def size(self):
        return len(self._tokens)


class _Pointer:

    _history: RecHistory
    _token_collection: _TokenCollection

    def __init__(self,
                 at_state: MatchState,
                 tokens: _TokenCollection,
                 current_position = 0,
                 history: RecHistory | None = None):
        self._at_state = at_state
        self._token_collection = tokens
        self._current_position = current_position
        if history is None:
            self._history = RecHistory()
        else:
            self._history = history

    def __eq__(self, other):
        if not isinstance(other, _Pointer):
            return False
        return self._at_state == other._at_state and self._history == other._history
    def __str__(self):
        return f"Pointer {self._at_state}"

    def get_state(self) -> MatchState:
        return self._at_state

    def _create_next_pointer(self, advanced_by: int, connection: MatchConnection) -> Self:
        new_position = self._current_position + advanced_by
        destination = self._at_state.get_destination(connection)
        new_item = HistoryItem(
            prev_state=self._at_state,
            connection=connection,
            prev_point=self._current_position,
            step=advanced_by
        )
        return _Pointer(
            at_state=destination,
            tokens=self._token_collection,
            current_position=new_position,
            history=self._history.extend(new_item)
        )


    def advance_with_analyzer(self, connection : MatchConnection, analyzer: GenericContextAnalyzer) -> List[Self]:

        result_pointers: List[_Pointer] = []
        index_before = self._current_position

        def _on_interrupt(ctx: RecognizeContext):
            if ctx.is_failed():
                return
            index_after = ctx.index()
            next_pointer = self._create_next_pointer(index_after - index_before, connection)
            result_pointers.append(next_pointer)

        context = RecognizeContext(self._token_collection.tokens(), _on_interrupt, start_at=self._current_position)
        analyzer.process(context)
        _on_interrupt(context)
        return result_pointers

    def auto_advance(self, connection: MatchConnection) -> List[Self]:
        return []

    def is_finished(self):
        return self._at_state.is_final() and self._current_position >= self._token_collection.size()

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
    __token_stream: None | _TokenCollection

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
        self._token_stream = _TokenCollection(arr)

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
    __token_stream : None | _TokenCollection
    def __init__(self, matcher: Matcher, text: str, definitions: MatchingDefinitionSet):
        self._reader = _TRReader(matcher, text, definitions)

    def recognize(self):
        reached_pointers = self._reader.recognize()







