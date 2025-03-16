from enum import Enum
from typing import List, Self

from src.miles.utils.decorators import auto_str
from src.miles.utils.list_utils import index_of


class NodeType(Enum):
    AUTOMATIC = 0
    MATCHING = 1
    WORD = 2


@auto_str
class NormalizedNode:
    def __init__(self, node_type : NodeType, argument: str, name: str | None):
        self.node_type = node_type
        self.argument = argument
        self.name = name
    def __eq__(self, other):
        if not isinstance(other, NormalizedNode):
            return False
        return (self.node_type == other.node_type and
                self.argument == other.argument and
                self.name == other.name)

class NormalizedConnection:
    _id : int
    _nodes: List[NormalizedNode]
    def __init__(self, _id: int, nodes_included: List[NormalizedNode] | None):
        self._id = _id
        if nodes_included is None:
            nodes_included = []
        self._nodes = nodes_included
    def __eq__(self, other):
        if not isinstance(other, NormalizedConnection):
            return False
        return self._id == other._id
    def get_id(self) -> int:
        return self._id
    def get_nodes(self):
        return list(self._nodes)

class NormalizedState:
    _id: int
    _connections: List[NormalizedConnection]
    _priorities: List[int]
    _destinations: List[Self]
    _final: bool
    def __init__(self, _id: int, final: bool):
        self._id = _id
        self._connections = []
        self._final = final
        self._priorities = []

    def add_connection(self, connection : NormalizedConnection, destination: Self, priority: int = 0):
        self._connections.append(connection)
        self._destinations.append(destination)
        self._priorities.append(priority)

    def all_connections(self) -> List[NormalizedConnection]:
        return list(self._connections)

    def _connection_index(self, connection : NormalizedConnection) -> int:
        return index_of(self._connections, connection)

    def get_destination(self, connection : NormalizedConnection) -> Self | None:
        index = self._connection_index(connection)
        if index < 0:
            return None
        return self._destinations[index]

    def get_priority(self, connection : NormalizedConnection):
        index = self._connection_index(connection)
        if index < 0:
            return None
        return self._priorities[index]

    def get_id(self) -> int:
        return self._id

    def __eq__(self, other):
        if not isinstance(other, NormalizedState):
            return False
        return self._id == other._id

class NormalizedMatcher:
    _initial: NormalizedState

    def __init__(self, initial_state: NormalizedState):
        self._initial = initial_state

    def initial_state(self) -> NormalizedState:
        return self._initial