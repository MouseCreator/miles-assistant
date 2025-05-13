
from src.miles.shared.context_analyzer import (WordContextAnalyzer, AutomaticContextAnalyzer,
                                               GenericContextAnalyzer)
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.normalized_matcher import HistoryNodeType


class AnalyzerProvider:
    def __init__(self, definitions: MatchingDefinitionSet):
        self.definitions = definitions

    def provide_analyzer(self, node_type: HistoryNodeType, argument: str | None) -> GenericContextAnalyzer:
        if node_type == HistoryNodeType.AUTOMATIC:
            return AutomaticContextAnalyzer()
        if node_type == HistoryNodeType.MATCHING:
            return self.definitions.get_matching(argument).analyzer()
        if node_type == HistoryNodeType.WORD:
            return WordContextAnalyzer(argument)
