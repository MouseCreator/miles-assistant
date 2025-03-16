from typing import Dict, List

from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer


def _definition_id(plugin: str | None, name: str | None):
    result = ''
    if plugin is not None:
        result += plugin
    result += '|'
    if name is not None:
        result += name
    return result

class MatchingDefinition:

    def __init__(self, analyzer: GenericContextAnalyzer, plugin: str, name: str):
        self._plugin = plugin
        self._name = name
        self._analyzer = analyzer

    def analyzer(self) -> GenericContextAnalyzer:
        return self._analyzer

    def name(self) -> str:
        return self._name

class MatchingDefinitionSet:
    _def_dict: Dict[str, MatchingDefinition]
    def __init__(self):
        self._def_dict = {}

    def append_definition(self, definition: MatchingDefinition):
        self._def_dict[definition.name()] = definition

    def append_all_definitions(self, definitions: List[MatchingDefinition]):
        for d in definitions:
            self.append_definition(d)


    def get_matching(self, name: str) -> MatchingDefinition:
        definition = self._def_dict.get(name)
        if definition is None:
            raise KeyError(f'No matching definition found for {name}')
        return definition



