from typing import Dict, List

from src.miles.core.recognizer.context_analyzer import TypedContextAnalyzer

class MatchingDefinition:

    def __init__(self, name: str, analyzer: TypedContextAnalyzer):
        self._name = name
        self._analyzer = analyzer

    def analyzer(self) -> TypedContextAnalyzer:
        return self._analyzer

    def name(self) -> str:
        return self._name

class MatchingDefinitionSet:
    _def_dict: Dict[str, MatchingDefinition]
    def __init__(self):
        self._def_dict = {}

    def append_definition(self, definition: MatchingDefinition):
        self._def_dict[ (definition.name() ) ] = definition

    def append_all_definitions(self, definitions: List[MatchingDefinition]):
        for d in definitions:
            self.append_definition(d)

    def get_matching(self, name: str) -> MatchingDefinition:
        _key = name
        definition = self._def_dict.get( _key )
        if definition is None:
            raise KeyError(f'No matching definition found for {_key}')
        return definition



