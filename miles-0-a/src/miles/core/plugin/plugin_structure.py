from typing import List

from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet


class NamespaceComponent:
    def __init__(self, name: str, namespace_matcher: NormalizedMatcher, command_mather: NormalizedMatcher):
        self.name = name
        self.namespace_matcher = namespace_matcher
        self.command_matcher = command_mather

class PluginStructure:
    def __init__(self, plugin_name : str, namespaces: List[NamespaceComponent], definitions: MatchingDefinitionSet):
        self.plugin_name = plugin_name
        self.namespaces = namespaces
        self.definitions = definitions