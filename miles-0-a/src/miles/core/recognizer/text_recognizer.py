import re
from typing import List, Self, Set

from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType, MatchConnection
from src.miles.core.recognizer.generic_recognizer import Recognizer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet, MatchingStrategy

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

    def __init__(self, at_state: MatchState,
                 history: List[_HistoryItem] | None = None):
        self._at_state = at_state

        if history is None:
            self._history = []
        else:
            self._history = list(history)

    def __eq__(self, other):
        if not isinstance(other, _Pointer):
            return False
        return self._at_state == other._at_state and self._history == other._history

    def is_same_state(self, other : Self):
        return self._at_state == other._at_state

    def move_to(self,
                conn: MatchConnection | None,
                new_state: MatchState,
                token: str | None,
                label: str | None = None) -> Self:
        item = _HistoryItem(self._at_state, conn, token, label)
        return _Pointer(new_state, self._history + [item])

    def get_state(self) -> MatchState:
        return self._at_state

    def __str__(self):
        return f"Pointer {self._at_state}"

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

class TextRecognizer(Recognizer):
    _pointers: List[_Pointer]
    _reached_pointers: List[_Pointer]
    __token_stream : None | _RecTokenStream
    def __init__(self, matcher: Matcher, text: str, definitions: MatchingDefinitionSet):
        self._matcher = matcher
        self._text = text
        self._token_stream = None
        self._pointers = []
        self._reached_pointers = []
        self._definitions = definitions

    def recognize(self):
        self._create_token_stream()
        self._recognize_tokens()
        return list(self._reached_pointers)

    def _create_token_stream(self):
        arr = re.split(r'\s+', self._text)
        self._token_stream = _RecTokenStream(arr)

    def _recognize_tokens(self):
        initial = self._matcher.get_initial_state()
        self._pointers.append(_Pointer(initial))

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
        while self._token_stream.has_tokens():
            current_token = self._token_stream.next_token()
            self._fill_automatic_paths()
            new_pointers: List[_Pointer] = []
            for p in self._pointers:
                state = p.get_state()

                for conn in state.all_connections():
                    # PRIORITY ?
                    conn_type = conn.connection_type
                    if conn_type == ConnectionType.AUTOMATIC:
                        continue
                    if conn_type == ConnectionType.WORD:
                        if self._is_word_matches(conn, current_token):
                            destination = state.get_destination(conn)
                            p_n = p.move_to(conn, destination, current_token)
                            new_pointers.append(p_n)

                    elif conn_type == ConnectionType.MATCHING:
                        matching_result = self._on_matchings(conn, current_token)
                        if matching_result.destroy:
                            continue
                        destination = state.get_destination(conn)
                        if matching_result.append:
                            label = None
                        else:
                            label = 'ignore'
                        if matching_result.move:
                            p_n = p.move_to(conn, destination, current_token, label)
                            new_pointers.append(p_n)
                        else:
                            p_n = p.move_to(None, state, current_token, label)
                            new_pointers.append(p_n)

                    else:
                        raise ValueError(f'Unknown connection type: {conn_type.name}')
            self._pointers = new_pointers

        # autocomplete all automatic paths after all tokens are consumed
        self._fill_automatic_paths()

    def _is_word_matches(self, conn: MatchConnection, current_token: str) -> bool:
        argument = conn.connection_arg
        return argument.upper() == current_token.upper()

    def _on_matchings(self, conn: MatchConnection, current_token: str) -> MatchingResult:
        plugin = conn.plugin
        name = conn.connection_arg
        matching = self._definitions.get_matching(plugin, name)

        matched = matching.matches(current_token)
        strategy = matching.get_strategy()

        if matched:
            if strategy == MatchingStrategy.MATCH_ONCE:
                return MatchingResult(move=True, append=True)
            if strategy == MatchingStrategy.KEEP_MATCHING:
                return MatchingResult(move=False, append=True)
            if strategy == MatchingStrategy.UNTIL_MATCHES_WAIT:
                return MatchingResult(move=True, append=True)
            if  strategy == MatchingStrategy.UNTIL_MATCHES_KEEP:
                return MatchingResult(move=False, append=True)
        else:
            if strategy == MatchingStrategy.MATCH_ONCE:
                return MatchingResult(destroy=True)
            if strategy == MatchingStrategy.KEEP_MATCHING:
                return MatchingResult(destroy=True)
            if strategy == MatchingStrategy.UNTIL_MATCHES_WAIT:
                return MatchingResult(move=False, append=False)
            if strategy == MatchingStrategy.UNTIL_MATCHES_KEEP:
                return MatchingResult(move=False, append=True)







