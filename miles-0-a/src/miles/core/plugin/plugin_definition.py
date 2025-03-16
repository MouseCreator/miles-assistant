from typing import List

from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.priority_manager import PriorityManager


class StoredCommand:
    def __init__(self, name: str, syntax: str):
        self.name = name
        self.syntax = syntax

class NamespaceOfCommands:
    def __init__(self, name: str, prefix: str, commands: List[StoredCommand]):
        self.name = name
        self.prefix = prefix
        self.commands = commands

class PluginDefinition:
    def __init__(self,
                 name: str,
                 namespaces: List[NamespaceOfCommands],
                 priority_manager: PriorityManager,
                 definition_set : MatchingDefinitionSet):
        self._namespaces = namespaces
        self._priority_manager = priority_manager
        self._name = name
        self._definition_set = definition_set
    def name(self):
        return self._name

    def namespaces(self):
        return list(self._namespaces)

    def get_priority_manager(self):
        return self._priority_manager

    def definition_set(self):
        return self._definition_set