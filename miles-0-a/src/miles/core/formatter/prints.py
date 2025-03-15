from typing import List

from src.miles.core.matcher.matcher import Matcher, MatchConnection, MatchState
from src.miles.utils.list_utils import index_of
from src.miles.utils.string_builder import StringBuilder


def _format_connection(connection: MatchConnection) -> str:
    return f'---{connection.sprint()}-->'

def _print_from_state(sb: StringBuilder, state: MatchState, space_level: int, visited: List[MatchState]):
    connections = state.all_connections()
    prev_index = index_of(visited, state)
    if prev_index >= 0:
        sb.append(f' [{prev_index}] ')
        return
    state_str = ' [] '
    space_level += len(state_str)
    sb.append(state_str)

    for i in range(len(connections)):
        conn = connections[i]
        if i != 0:
            sb.append('\n')
            sb.append(' ' * space_level)
        connection_str = _format_connection(conn)
        sb.append(connection_str)
        spaces = space_level + len(connection_str)
        dest = state.get_destination(conn)
        _print_from_state(sb, dest, spaces, visited + [state])

def print_matcher(matcher: Matcher) -> str:
    initial_state = matcher.get_initial_state()
    sb = StringBuilder()
    _print_from_state(sb, initial_state, 0, [])
    return sb.to_string()