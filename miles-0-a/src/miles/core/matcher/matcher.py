
from typing import Self, List


from src.miles.core.matcher.matcher_error import MatcherError
from src.miles.utils.list_utils import index_of
from src.miles.utils.pretty import PrintableStructure
from src.miles.utils.strings import print_list
from src.miles.shared.connection_type import ConnectionType


class MatchConnection(PrintableStructure):
    connection_type: ConnectionType
    connection_arg: str | None
    name: str
    def __init__(self, connection_type: ConnectionType, connection_arg: str | None, name: str | None=None):
        self.connection_type = connection_type
        self.connection_arg = connection_arg
        self.name = name

    def __str__(self):
        return f"MatchConnection {{ {self.connection_type.name}, {self.connection_arg}, {self.name} }}"

    def __eq__(self, other):
        if not isinstance(other, MatchConnection):
            return False
        return (self.name == other.name
                and self.connection_type == other.connection_type
                and self.connection_arg == other.connection_arg)

    def sprint(self):
        result = '(' + self.connection_type.name
        if self.connection_arg:
            result += ', '
            result += self.connection_arg
        if self.name:
            result += ', '
            result += self.connection_arg
        result += ')'
        return result

class MatchState:
    _state_id: int
    _connections: List[MatchConnection]
    _destinations: List[Self]
    _priorities: List[int]
    _final: bool

    def __hash__(self):
        return self._state_id

    def __init__(self, state_id: int, is_final: bool = False):
        self._state_id = state_id
        self._connections = []
        self._destinations = []
        self._priorities = []
        self._final = is_final

    def __str__(self):
        return (f"State {{ id={self._state_id}, "
                f"connections={print_list(self._connections)}, "
                f"destinations={print_list([t._state_id for t in self._destinations])}, "
                f"priorities={print_list(self._priorities)}}}")

    @classmethod
    def initial(cls) -> Self:
        return MatchState(0)

    def __eq__(self, other):
        if not isinstance(other, MatchState):
            return False
        return self._state_id == other._state_id

    def has_connection(self, connection: MatchConnection, priority: int | None=None):
        index = index_of(self._connections, connection)
        if index == -1:
            return False
        if priority is None:
            return True
        return self._priorities[index] == priority

    def get_destination(self, connection):
        index = index_of(self._connections, connection)
        if index < 0:
            return None
        return self._destinations[index]

    def get_priority(self, connection: MatchConnection):
        index = index_of(self._connections, connection)
        if index < 0:
            return None
        return self._priorities[index]

    def all_connections(self) -> List[MatchConnection]:
        return list(self._connections)

    def update_priority(self, connection: MatchConnection, priority: int):
        index = index_of(self._connections, connection)
        if index == -1:
            return None

        if self._priorities[index] < priority:
            self._priorities[index] = priority
        return self._destinations[index]

    def add_connection(self, connection: MatchConnection, priority:int, new_state: Self):
        if self.has_connection(connection):
            raise MatcherError(f'Cannot add connection, because one already exists: {connection}')
        self._connections.append(connection)
        self._priorities.append(priority)
        self._destinations.append(new_state)
        return new_state
    def is_final(self):
        return self._final

    def get_id(self) -> int:
        return self._state_id


class Matcher:
    def __init__(self, initial_state: MatchState):
        self._initial_state = initial_state

    def get_initial_state(self) -> MatchState:
        return self._initial_state









