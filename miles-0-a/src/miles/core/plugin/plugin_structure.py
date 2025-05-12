from typing import List

from src.miles.core.priority.dynamic_priority import DynamicPriorityRuleSet
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet


class NamespaceComponent:
    def __init__(self,
                 name: str,
                 command_mather: NormalizedMatcher,
                 definitions: MatchingDefinitionSet,
                 dynamic_ruleset: DynamicPriorityRuleSet):
        self.name = name
        self.command_matcher = command_mather
        self.definitions = definitions
        self.dynamic_priorities = dynamic_ruleset


class PluginStructure:
    def __init__(self, plugin_name : str, namespaces: List[NamespaceComponent]):
        self.plugin_name = plugin_name
        self.namespaces = namespaces