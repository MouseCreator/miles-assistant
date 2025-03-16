from typing import Dict, List, Tuple

from src.miles.core.context.data_types import InputDataType
from src.miles.core.recognizer.context_analyzer import TypedContextAnalyzer

class MatchingDefinition:

    def __init__(self, analyzer: TypedContextAnalyzer, plugin: str, datatype: InputDataType, name: str):
        self._plugin = plugin
        self._name = name
        self._analyzer = analyzer
        self._datatype = datatype

    def analyzer(self) -> TypedContextAnalyzer:
        return self._analyzer

    def name(self) -> str:
        return self._name

    def datatype(self) -> InputDataType:
        return self._datatype
    def plugin(self) -> str:
        return self._plugin

class MatchingDefinitionSet:
    _def_dict: Dict[Tuple[str, InputDataType, str], MatchingDefinition]
    def __init__(self):
        self._def_dict = {}


    def append_definition(self, definition: MatchingDefinition):
        self._def_dict[ (definition.plugin(), definition.datatype(), definition.name() ) ] = definition

    def append_all_definitions(self, definitions: List[MatchingDefinition]):
        for d in definitions:
            self.append_definition(d)

    def get_matching(self, plugin: str, datatype: InputDataType, name: str) -> MatchingDefinition:
        _key = (plugin, datatype, name)
        definition = self._def_dict.get( _key )
        if definition is None:
            raise KeyError(f'No matching definition found for {_key}')
        return definition



