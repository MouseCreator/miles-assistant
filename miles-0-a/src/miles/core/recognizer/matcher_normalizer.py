from typing import Set, List, Self

from src.miles.core.matcher.matcher import Matcher, MatchState, MatchConnection, ConnectionType


class NormalizedMatcher:
    """
    For priority control, it will be essential to use Normalized Matchers.
    Normalized matchers will have complex connections, that contain multiple actions
    This approach provides several important advantages:
        - easier to calculate priorities. Taking max() or first non-zero priority from the group is easier,
        when connections are normalized;
        - No redundant connections that result in an infinite loop.
        For example, [{a}] - list of optionals may have an infinite loop
        - Automatic connections are still possible because of final states.
        For example, (state) --auto--> (final) cannot be rewritten as word or matching connection
    Challenges:
        - Normalization algorithm
        - Adjust text recognized to handle complex connections properly
    """
    pass

class _PathNode:
    def __init__(self, state: MatchState, connection : MatchConnection):
        self.state = state
        self.connection = connection

class _Path:
    def __init__(self, path: List[_PathNode] | None = None):
        self._path = path

    def extend(self, node: _PathNode) -> Self:
        return _Path(self._path + [node])

    def destination(self) -> MatchState | None:
        if len(self._path) == 0:
            return None
        last_node = self._path[-1]
        return last_node.state.get_destination(last_node.connection)


class _StackItem:
    def __init__(self, state: MatchState, count: int, path: _Path):
        self.state = state
        self.count = count
        self.path = path





def _find_all_reachable_paths(from_state: MatchState) -> List[_Path]:
    stack: List[_StackItem] = [_StackItem(from_state, 0, _Path())]
    paths: List[_Path] = []
    while len(stack) > 0:
        current = stack[-1]
        connections = current.state.all_connections()

        if current.count >= len(connections):
            stack.pop(-1)

        connection = current.state.all_connections()[current.count]
        destination = current.state.get_destination(connection)

        terminate = False

        if connection.connection_type != ConnectionType.AUTOMATIC:
            terminate = True
        if destination.is_final():
            terminate = True

        if destination in stack: # loopback
            continue

        new_path = current.path.extend(_PathNode(current.state, connection))

        if terminate:
            paths.append(new_path) # reached final state, remember the path and continue
        else:
            stack.append(_StackItem(destination, 0, new_path)) # continue from this node
    return paths

class _NormalizedPaths:
    def __init__(self, origin: MatchState, paths: List[_Path]):
        self.origin = origin
        self.paths = paths

def normalize(matcher: Matcher):
    initial = matcher.get_initial_state()
    key_states: Set[MatchState] = { initial }

    queue: List[MatchState] = [ initial ]
    n_paths: List[_NormalizedPaths] = []
    while len(queue) > 0:
        current = queue.pop(0)
        reachable: List[_Path] = _find_all_reachable_paths(current)

        last_destinations = []
        for r in reachable:
            last_destinations.append( r.destination() )

        for dest in last_destinations:
            if dest not in key_states:
                queue.append(dest)

        key_states = key_states | set(last_destinations)
        n_paths.append(_NormalizedPaths(current, reachable))

