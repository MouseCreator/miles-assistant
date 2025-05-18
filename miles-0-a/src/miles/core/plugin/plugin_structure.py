from typing import List

from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher
from src.miles.shared.certainty import CertaintyEffect
from src.miles.shared.context_analyzer import WordContextAnalyzerFactory
from src.miles.shared.executor.command_executor import CommandExecutorsMap
from src.miles.shared.priority.dynamic_priority import DynamicPriorityRuleSet


class NamespaceComponent:
    def __init__(self,
                 name: str,
                 command_mather: NormalizedMatcher,
                 definitions: MatchingDefinitionSet,
                 dynamic_ruleset: DynamicPriorityRuleSet,
                 executors_map: CommandExecutorsMap,
                 word_analyzer_factory: WordContextAnalyzerFactory,
                 certainty_effect: CertaintyEffect):
        self.name = name
        self.executors_map = executors_map
        self.command_matcher = command_mather
        self.definitions = definitions
        self.dynamic_priorities = dynamic_ruleset
        self.word_analyzer_factory = word_analyzer_factory
        self.certainty_effect = certainty_effect


class PluginStructure:
    def __init__(self, plugin_name: str, namespaces: List[NamespaceComponent]):
        self.plugin_name = plugin_name
        self.namespaces = namespaces
