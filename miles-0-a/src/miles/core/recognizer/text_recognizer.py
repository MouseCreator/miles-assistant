from typing import List, Self

from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType, MatchConnection
from src.miles.core.recognizer.generic_recognizer import Recognizer

class _Pointer:
    def __init__(self, at_state: MatchState):
        self._at_state = at_state

    def __eq__(self, other):
        if not isinstance(other, _Pointer):
            return False
        return self._at_state == other._at_state

    def move_to(self, new_state: MatchState) -> Self:
        return _Pointer(new_state)

    def get_state(self) -> MatchState:
        return self._at_state

    def __str__(self):
        return f"Pointer {self._at_state}"

class _RecTokenStream:
    def __init__(self):
        pass
    def next_token(self) -> str:
        return ""

class TextRecognizer(Recognizer):
    _pointers: List[_Pointer]
    __token_stream : None | _RecTokenStream
    def __init__(self, matcher: Matcher, text: str, expressions):
        self._matcher = matcher
        self._text = text
        self._token_stream = None
        self._pointers = []
        self._expressions = expressions

    def recognize(self):
        self._create_token_stream()
        return self._recognize_tokens()

    def _create_token_stream(self):
        return self._text.split(' ')

    def _recognize_tokens(self):
        initial = self._matcher.get_initial_state()
        self._pointers.append(_Pointer(initial))
        while True:
            current_token = self._token_stream.next_token()
            new_pointers = []
            for p in self._pointers:
                state = p.get_state()
                for conn in state.all_connections():
                    # PRIORITY ?
                    conn_type = conn.connection_type
                    if conn_type == ConnectionType.AUTOMATIC:
                        destination = state.get_destination(conn)
                        new_pointers.append(p.move_to(destination))
                    elif conn_type == ConnectionType.WORD:
                        if self._is_word_matches(conn, current_token):
                            destination = state.get_destination(conn)
                            new_pointers.append(p.move_to(destination))
                    elif conn_type == ConnectionType.MATCHING:
                        destinations = self._on_matchings(conn, current_token)
                        new_pointers.extend(destinations)
                    else:
                        raise ValueError(f'Unknown connection type: {conn_type.name}')
            self._pointers = new_pointers

    def _is_word_matches(self, conn: MatchConnection, current_token: str) -> bool:
        pass

    def _on_matchings(self, conn, current_token) -> List[MatchState]:
        pass



