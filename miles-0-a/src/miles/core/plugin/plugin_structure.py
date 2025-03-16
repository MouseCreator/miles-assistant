from typing import List

from src.miles.core.normalized.normalized_matcher import NormalizedMatcher, NormalizedConnection


class NamespaceComponent:
    def __init__(self, name: str, namespace_matcher: NormalizedMatcher, command_mather: NormalizedMatcher):
        self.name = name
        self.namespace_matcher = namespace_matcher
        self.command_matcher = command_mather

class PluginStructure:
    def __init__(self, plugin_name : str, namespaces: List[NormalizedConnection]):
        self.plugin_name = plugin_name
        self.namespaces = namespaces