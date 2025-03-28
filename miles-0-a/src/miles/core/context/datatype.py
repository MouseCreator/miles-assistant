
from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeVar, Generic, List, Any

from src.miles.core.context.data_holder import InputDataHolder, TextDataHolder
from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer, AutomaticContextAnalyzer, \
    WordContextAnalyzer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.normalized_matcher import NodeType

T = TypeVar('T')
S = TypeVar('S')


class AbstractDataType(Generic[T, S], ABC):
    pass

class OriginType(Enum):
    TEXT_DATA = 0
    SOUND_DATA = 1

class DataTypeManager(Generic[T]):
    definitions: MatchingDefinitionSet
    def __init__(self, definitions: MatchingDefinitionSet):
        self.definitions = definitions
    @abstractmethod
    def origin_type(self) -> OriginType:
        pass
    @abstractmethod
    def prepare(self, raw_data: Any) -> List[T]:
        pass
    @abstractmethod
    def dataholder(self, tokens: List[T]) -> InputDataHolder:
        pass
    @abstractmethod
    def provide_analyzer(self, node_type: NodeType, argument: str | None) -> GenericContextAnalyzer:
        pass


class TextTypeManager(DataTypeManager[str]):

    def origin_type(self):
        return OriginType.TEXT_DATA

    def prepare(self, source_data: str) -> List[str]:
        return source_data.split()

    def dataholder(self, tokens: List[str]) -> InputDataHolder:
        return TextDataHolder(tokens)

    def provide_analyzer(self, node_type: NodeType, argument: str | None) -> GenericContextAnalyzer:
        if node_type == NodeType.AUTOMATIC:
            return AutomaticContextAnalyzer()
        if node_type == NodeType.MATCHING:
            return self.definitions.get_matching(argument).analyzer()
        if node_type == NodeType.WORD:
            return WordContextAnalyzer(argument)




