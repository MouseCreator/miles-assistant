from typing import List

from src.miles.core.matcher.matcher import Matcher, MatchState, ConnectionType, MatchConnection
from src.miles.core.recognizer.priority import PriorityManager


class _Path:
    def __init__(self, from_state: MatchState, connection: MatchConnection):
        self.from_state = from_state
        self.connection = connection
    def __eq__(self, other):
        if not isinstance(other, _Path):
            return False
        return self.from_state == other.from_state and self.connection == other.connection

class PriorityAssigner:

    def __init__(self, matcher: Matcher, priority_manager: PriorityManager):
        self._matcher = matcher
        self._priority_manager = priority_manager

    def _all_auto_paths(self) -> List[_Path]:
        initial_state = self._matcher.get_initial_state()
        visited_states = { initial_state }
        queue = [ initial_state ]
        result = []
        while len(queue) > 0:
            current = queue.pop(0)
            all_connections = current.all_connections()
            for connection in all_connections:
                if connection.connection_type == ConnectionType.AUTOMATIC:
                    result.append(_Path(current, connection))
                    dest = current.get_destination(connection)
                    if dest not in visited_states:
                        visited_states.add(dest)
                        queue.append(dest)
        return result

    def _set_individual_priorities(self):
        paths = self._all_auto_paths()
        for path in paths:
            priority = self._priority_manager.get_priority(path.connection)
            path.from_state.update_priority(path.connection, priority)

    def assign_all(self):
        self._set_individual_priorities()




