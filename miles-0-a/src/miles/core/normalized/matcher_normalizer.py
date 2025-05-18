from typing import Set, List, Self, Dict

from src.miles.core.matcher.matcher import Matcher, MatchState, MatchConnection, ConnectionType
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher, NormalizedState, NormalizedNode, \
    HistoryNodeType, \
    NormalizedConnection
from src.miles.utils.decorators import auto_str
from src.miles.utils.pretty import PrintableStructure
from src.miles.utils.string_builder import StringBuilder
from src.miles.utils.strings import print_list

"""
For priority control, it is essential to use Normalized Matchers.
Normalized matchers have complex connections, that contain multiple actions
This approach provides several important advantages:
    - easier to calculate priorities. Taking max() or first non-zero priority from the group is easier,
    when connections are normalized;
    - No redundant connections that result in an infinite loop.
    For example, [{a}] - list of optionals may have an infinite loop
    - Automatic connections are still possible because of final states.
    For example, (state) --auto--> (final) cannot be rewritten as word or matching connection
"""


@auto_str
class _PathNode:
    def __init__(self, state: MatchState, connection: MatchConnection):
        self.state = state
        self.connection = connection


class _Path:
    def __init__(self, path: List[_PathNode] | None = None):
        if path is None:
            path = []
        self._path = path

    def extend(self, node: _PathNode) -> Self:
        return _Path(self._path + [node])

    def destination(self) -> MatchState | None:
        if len(self._path) == 0:
            return None
        last_node = self._path[-1]
        return last_node.state.get_destination(last_node.connection)

    def __str__(self):
        return print_list(self._path)

    def nodes(self) -> List[_PathNode]:
        return list(self._path)


@auto_str
class _StackItem:
    def __init__(self, state: MatchState, count: int, path: _Path):
        self.state = state
        self.count = count
        self.path = path


class _NormalizedPaths(PrintableStructure):
    def sprint(self):
        sb = StringBuilder()
        sb.append(self.origin.get_id()).append(" ->\n")
        for i in range(len(self.paths)):
            path = self.paths[i]
            for node in path.nodes():
                sb.append(node.connection.connection_arg)
            sb.append(f" -- {path.destination().get_id()}")
            if i != len(self.paths) - 1:
                sb.append("\n")
        return sb.to_string()

    def __init__(self, origin: MatchState, paths: List[_Path]):
        self.origin = origin
        self.paths = paths

    def __str__(self):
        return f"Normalized Path: {self.origin} -> {print_list(self.paths)}"


class _NormalizedCollection(PrintableStructure):
    def __init__(self, paths: List[_NormalizedPaths]):
        self._paths = paths

    def sprint(self):
        lst = []
        for p in self._paths:
            lst.append(p.sprint())
        return "\n".join(lst)

    def all_paths(self) -> List[_NormalizedPaths]:
        return list(self._paths)


def _find_all_reachable_paths(from_state: MatchState) -> List[_Path]:
    stack: List[_StackItem] = [_StackItem(from_state, 0, _Path())]
    paths: List[_Path] = []
    while len(stack) > 0:
        current = stack[-1]
        connections = current.state.all_connections()

        if current.count >= len(connections):
            stack.pop(-1)
            continue

        connection = current.state.all_connections()[current.count]
        destination = current.state.get_destination(connection)
        current.count += 1

        terminate = False

        if connection.connection_type != ConnectionType.AUTOMATIC:
            terminate = True
        if destination.is_final():
            terminate = True

        if destination in [s.state for s in stack] and not terminate:  # loopback
            continue

        new_path = current.path.extend(_PathNode(current.state, connection))

        if terminate:
            paths.append(new_path)  # reached final state, remember the path and continue
        else:
            stack.append(_StackItem(destination, 0, new_path))  # continue from this node
    return paths


def _get_normalized_collection(matcher: Matcher) -> _NormalizedCollection:
    initial = matcher.get_initial_state()
    key_states: Set[MatchState] = {initial}

    queue: List[MatchState] = [initial]
    n_paths: List[_NormalizedPaths] = []
    while len(queue) > 0:
        current = queue.pop(0)
        reachable: List[_Path] = _find_all_reachable_paths(current)

        last_destinations = []
        for r in reachable:
            last_destinations.append(r.destination())

        for dest in last_destinations:
            if dest not in key_states:
                queue.append(dest)

        key_states = key_states | set(last_destinations)
        if len(reachable) > 0:
            n_paths.append(_NormalizedPaths(current, reachable))

    return _NormalizedCollection(n_paths)


class _ConnectionPrototype:
    def __init__(self, from_id: int, path: _Path, to_id: int):
        self.from_id = from_id
        self.to_id = to_id
        self.path = path


def _map_connection_type(connection_type: ConnectionType) -> HistoryNodeType:
    if connection_type == ConnectionType.AUTOMATIC:
        return HistoryNodeType.AUTOMATIC
    if connection_type == ConnectionType.MATCHING:
        return HistoryNodeType.MATCHING
    if connection_type == ConnectionType.WORD:
        return HistoryNodeType.WORD


class _NormalizerMatcherBuilder:
    def __init__(self, origin_id: int, collection: _NormalizedCollection):
        self._state_id = origin_id
        self._origin_id = origin_id
        self._collection = collection
        self._connection_id = 0

    def _create_state(self, _final: bool):
        state = NormalizedState(self._state_id, _final)
        self._state_id += 1
        return state

    def build(self) -> NormalizedMatcher:
        paths = self._collection.all_paths()

        prototypes: List[_ConnectionPrototype] = []

        all_states: Dict[int, NormalizedState] = {}

        for path in paths:
            origin = path.origin
            for inner in path.paths:
                destination = inner.destination()
                prototypes.append(_ConnectionPrototype(origin.get_id(), inner, destination.get_id()))
                if origin.get_id() not in all_states.keys():
                    all_states[origin.get_id()] = self._create_state(origin.is_final())
                if destination.get_id() not in all_states.keys():
                    all_states[destination.get_id()] = self._create_state(destination.is_final())

        for prototype in prototypes:
            from_state = all_states.get(prototype.from_id)
            to_state = all_states.get(prototype.to_id)
            all_nodes = []
            for path_node in prototype.path.nodes():
                connection = path_node.connection
                normalized_node = NormalizedNode(
                    _map_connection_type(connection.connection_type),
                    connection.connection_arg,
                    connection.name
                )
                all_nodes.append(normalized_node)
            normalized_connection = NormalizedConnection(self._connection_id, all_nodes)
            self._connection_id += 1
            from_state.add_connection(normalized_connection, to_state)

        return NormalizedMatcher(all_states.get(self._origin_id))


def _build_normalized_matcher(matcher: Matcher, collection: _NormalizedCollection) -> NormalizedMatcher:
    origin_id = matcher.get_initial_state().get_id()
    return _NormalizerMatcherBuilder(origin_id, collection).build()


def normalize(origin: Matcher) -> NormalizedMatcher:
    collection = _get_normalized_collection(origin)
    return _build_normalized_matcher(origin, collection)
