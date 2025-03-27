from abc import ABC, abstractmethod
from typing import List

from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher, NormalizedConnection, NormalizedState
from src.miles.core.priority.priority_manager import PriorityManager, PriorityStrategy


class _Path:
    def __init__(self, state: NormalizedState, connection: NormalizedConnection):
        self.state = state
        self.connection = connection

class ConnectionPrioritizer(ABC):
    @abstractmethod
    def get_priority(self, plugin: str, priority_manager: PriorityManager, connection: NormalizedConnection) -> int:
        pass

class FirstConnectionPrioritizer(ConnectionPrioritizer):
    def get_priority(self, plugin: str, priority_manager: PriorityManager, connection: NormalizedConnection) -> int:
        if connection.empty():
            return priority_manager.default_priority()
        first = connection.get_nodes()[0]
        return priority_manager.get_priority(plugin, first)

class FindMaxConnectionPrioritizer(ConnectionPrioritizer):
    def get_priority(self, plugin: str, priority_manager: PriorityManager, connection: NormalizedConnection) -> int:
        if connection.empty():
            return priority_manager.default_priority()
        priorities = map(lambda c: priority_manager.get_priority(plugin, c) ,connection.get_nodes())
        return max(priorities)

class AllDefaultConnectionPrioritizer(ConnectionPrioritizer):
    def get_priority(self, plugin: str, priority_manager: PriorityManager, connection: NormalizedConnection) -> int:
        return priority_manager.default_priority()


def _prioritizer(strategy: PriorityStrategy) -> ConnectionPrioritizer:
    if strategy == PriorityStrategy.FIRST:
        return FirstConnectionPrioritizer()
    if strategy == PriorityStrategy.FIND_MAX:
        return FindMaxConnectionPrioritizer()
    if strategy == PriorityStrategy.ALL_DEFAULT:
        return AllDefaultConnectionPrioritizer()
    raise ValueError(f'Unknown strategy prioritizer strategy: {strategy}')

class PriorityAssigner:

    def __init__(self, priority_manager: PriorityManager):
        self._priority_manager = priority_manager

    def _all_paths(self, matcher: NormalizedMatcher) -> List[_Path]:
        states = self._all_states(matcher)
        result: List[_Path] = []
        for state in states:
            for connection in state.all_connections():
                result.append(_Path(state, connection))
        return result

    def _all_states(self, matcher) -> List[NormalizedState]:
        initial_state = matcher.initial_state()
        visited_states = {initial_state}
        queue = [initial_state]
        while len(queue) > 0:
            current = queue.pop(0)
            all_connections = current.all_connections()
            for connection in all_connections:
                dest = current.get_destination(connection)
                if dest not in visited_states:
                    visited_states.add(dest)
                    queue.append(dest)
        return list(visited_states)

    def _assign_priorities(self, plugin: str, matcher: NormalizedMatcher, strategy: PriorityStrategy):
        paths = self._all_paths(matcher)
        for path in paths:
            priority = self._get_priority_for(plugin, path.connection, strategy)
            path.state.update_priority(path.connection, priority)

    def _get_priority_for(self, plugin: str, connection: NormalizedConnection, strategy: PriorityStrategy) -> int:
        prioritizer = _prioritizer(strategy)
        return prioritizer.get_priority(plugin, self._priority_manager, connection)


    def _refresh_priorities(self, matcher):
        states: List[NormalizedState] = self._all_states(matcher)
        for state in states:
            for conn in state.all_connections():
                state.update_priority(conn, self._priority_manager.default_priority())

    def assign_all(self, plugin: str, matcher: NormalizedMatcher):
        self._refresh_priorities(matcher)
        self._assign_priorities(plugin, matcher, self._priority_manager.get_strategy())






