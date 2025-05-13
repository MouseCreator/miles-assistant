from typing import List

from src.miles.core.command.generic_command_processor import GenericCommandProcessor
from src.miles.shared.executor import CommandExecutorsMap

from src.miles.core.matcher.matcher_factory import MatcherFactory
from src.miles.core.normalized.matcher_normalizer import normalize
from src.miles.core.plugin.plugin_definition import PluginDefinition
from src.miles.core.plugin.plugin_structure import PluginStructure, NamespaceComponent
from src.miles.core.priority.priority_assign import PriorityAssigner
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher


def create_normalized_matcher_from_definitions(plugin_definition: PluginDefinition) -> PluginStructure:
    plugin_name = plugin_definition.name()

    matcher_factory = MatcherFactory()
    namespace_components: List[NamespaceComponent] = []
    for namespace in plugin_definition.namespaces():

        priority_manager = namespace.priority_manager
        dynamic_rule_set = namespace.dynamic_priorities
        priority_assigner = PriorityAssigner(priority_manager)

        matcher = matcher_factory.empty_matcher()
        for stored_command in namespace.commands:
            command = GenericCommandProcessor().process(stored_command.syntax)
            matcher_factory.add_command(matcher, command, stored_command.name)

        normalized_matcher = normalize(matcher)

        executor_map = CommandExecutorsMap()
        for stored_command in namespace.commands:
            executor_map.add(stored_command.name, stored_command.executor)

        priority_assigner.assign_all(normalized_matcher)
        namespace_component = NamespaceComponent(namespace.name,
                                                 normalized_matcher,
                                                 namespace.definition_set,
                                                 dynamic_rule_set,
                                                 executor_map)
        namespace_components.append(namespace_component)

    return PluginStructure(plugin_name, namespace_components)


def create_normalized_matcher_for_namespaces(all_plugins: List[PluginDefinition]) -> NormalizedMatcher:
    matcher_factory = MatcherFactory()
    matcher = matcher_factory.empty_matcher()
    for plugin in all_plugins:
        for namespace in plugin.namespaces():
            component = namespace.as_command_namespace()
            matcher_factory.create_namespace(matcher, component)
    return normalize(matcher)

