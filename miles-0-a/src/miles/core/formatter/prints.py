
from src.miles.core.matcher.matcher import Matcher, MatchConnection, MatchState
from src.miles.utils.string_builder import StringBuilder


def _format_connection(connection: MatchConnection) -> str:
    return f'---{connection.sprint()}-->'

def _print_from_state(sb: StringBuilder, state: MatchState, space_level: int):
    connections = state.all_connections()
    state_str = ' [] '
    state_len = len(state_str)
    sb.append(state_str)
    for i in range(len(connections)):
        conn = connections[i]
        if i != 0:
            sb.append('\n')
            sb.append(' ' * space_level)
        connection_str = _format_connection(conn)
        state.get_priority(conn)
        sb.append(connection_str)
        spaces = space_level + len(connection_str) + state_len
        dest = state.get_destination(conn)
        _print_from_state(sb, dest, spaces)

def print_matcher(matcher: Matcher) -> str:
    initial_state = matcher.get_initial_state()
    sb = StringBuilder()
    _print_from_state(sb, initial_state, 0)
    return sb.to_string()