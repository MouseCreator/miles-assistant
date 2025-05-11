
from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeVar, Generic, List, Any

from src.miles.core.context.data_holder import InputDataHolder, TextDataHolder
from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer, AutomaticContextAnalyzer, \
    WordContextAnalyzer, TextContextAnalyzer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet, MatchingDefinition

T = TypeVar('T')
S = TypeVar('S')


class AbstractDataType(Generic[T, S], ABC):
    pass

class OriginType(Enum):
    TEXT_DATA = 0
    SOUND_DATA = 1

class DataTypeManager(Generic[T]):
    definitions: MatchingDefinitionSet
    def __init__(self):
        self.definitions = MatchingDefinitionSet()
        self.definitions.append_all_definitions(self.include_definitions())
        
    @abstractmethod
    def origin_type(self) -> OriginType:
        pass

    @abstractmethod
    def prepare(self, raw_data: Any) -> List[T]:
        pass

    @abstractmethod
    def dataholder(self, tokens: List[T]) -> InputDataHolder:
        pass

    def include_definitions(self) -> List[MatchingDefinition]:
        return []

    @abstractmethod
    def on_word(self, argument) -> GenericContextAnalyzer:
        pass

    def on_matching(self, argument) -> GenericContextAnalyzer:
        return self.definitions.get_matching(argument).analyzer()

    def on_automatic(self, argument) -> GenericContextAnalyzer:
        return AutomaticContextAnalyzer()

class TextTypeManager(DataTypeManager[str]):

    def origin_type(self):
        return OriginType.TEXT_DATA

    def prepare(self, source_data: str) -> List[str]:
        return source_data.split()

    def dataholder(self, tokens: List[str]) -> InputDataHolder:
        return TextDataHolder(tokens)

    def on_word(self, argument) -> GenericContextAnalyzer:
        return WordContextAnalyzer(argument)

    def include_definitions(self) -> List[MatchingDefinition]:
        return [ MatchingDefinition("text", TextContextAnalyzer()) ] # move to plugin ?





