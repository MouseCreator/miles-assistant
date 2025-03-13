from enum import Enum
from typing import Callable, Dict, List


class MatchingStrategy(Enum):
    MATCH_ONCE = 0
    KEEP_MATCHING = 1
    UNTIL_MATCHES_WAIT = 2
    UNTIL_MATCHES_KEEP = 3


def _definition_id(plugin: str | None, name: str | None):
    result = ''
    if plugin is not None:
        result += plugin
    result += '|'
    if name is not None:
        result += name
    return result

class MatchingDefinition:

    def __init__(self, test_function: Callable[[str], bool], plugin: str, name: str, strategy: MatchingStrategy):
        self._plugin = plugin
        self._name = name
        self._strategy = strategy
        self._test_function = test_function

    def get_strategy(self) -> MatchingStrategy:
        return self._strategy

    def matches(self, token: str) -> bool:
        return self._test_function(token)

    def name(self) -> str:
        return self._name

    def plugin(self) -> str:
        return self._plugin

    def definition_id(self) -> str:
        return _definition_id(self._plugin, self._name)


class MatchingDefinitionSet:
    _def_dict: Dict[str, MatchingDefinition]
    def __init__(self):
        self._def_dict = {}

    def append_definition(self, definition: MatchingDefinition):
        d_id = definition.definition_id()
        self._def_dict[d_id] = definition

    def append_all_definitions(self, definitions: List[MatchingDefinition]):
        for d in definitions:
            self.append_definition(d)


    def get_matching(self, plugin: str, name: str) -> MatchingDefinition:
        identifier = _definition_id(plugin, name)
        definition = self._def_dict.get(identifier)
        if definition is None:
            raise KeyError(f'No matching definition found for {identifier}')
        return definition



