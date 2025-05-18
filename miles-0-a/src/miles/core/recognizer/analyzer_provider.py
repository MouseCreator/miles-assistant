from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.normalized_matcher import HistoryNodeType
from src.miles.shared.context_analyzer import (AutomaticContextAnalyzer,
                                               GenericContextAnalyzer, WordContextAnalyzerFactory)


class AnalyzerProvider:
    def __init__(self, definitions: MatchingDefinitionSet, word_analyzer_factory: WordContextAnalyzerFactory):
        self.definitions = definitions
        self.word_analyzer_factory = word_analyzer_factory

    def provide_analyzer(self, node_type: HistoryNodeType, argument: str | None) -> GenericContextAnalyzer:
        if node_type == HistoryNodeType.AUTOMATIC:
            return AutomaticContextAnalyzer()
        if node_type == HistoryNodeType.MATCHING:
            return self.definitions.get_matching(argument).analyzer()
        if node_type == HistoryNodeType.WORD:
            return self.word_analyzer_factory.build(argument)
