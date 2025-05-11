
from src.miles.core.recognizer.context_analyzer import (WordContextAnalyzer, AutomaticContextAnalyzer,
                                                        GenericContextAnalyzer)
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.normalized_matcher import NodeType


class AnalyzerProvider:
    def __init__(self, definitions: MatchingDefinitionSet):
        self.definitions = definitions

    def provide_analyzer(self, node_type: NodeType, argument: str | None) -> GenericContextAnalyzer:
        if node_type == NodeType.AUTOMATIC:
            return AutomaticContextAnalyzer()
        if node_type == NodeType.MATCHING:
            return self.definitions.get_matching(argument).analyzer()
        if node_type == NodeType.WORD:
            return WordContextAnalyzer(argument)
