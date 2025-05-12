from typing import List

from src.miles.core.command.generic_command_processor import GenericCommandProcessor

from src.miles.core.matcher.matcher_factory import MatcherFactory
from src.miles.core.normalized.matcher_normalizer import normalize
from src.miles.core.plugin.plugin_definition import PluginDefinition
from src.miles.core.plugin.plugin_structure import PluginStructure, NamespaceComponent
from src.miles.core.priority.priority_assign import PriorityAssigner


def create_normalized_matcher_from_command_string(plugin_definition: PluginDefinition) -> PluginStructure:
    plugin_name = plugin_definition.name()

    matcher_factory = MatcherFactory()
    namespace_components: List[NamespaceComponent] = []
    for namespace in plugin_definition.namespaces():

        priority_manager = namespace.priority_manager
        dynamic_rule_set = namespace.dynamic_priorities
        priority_assigner = PriorityAssigner(priority_manager)

        namespace_matcher = matcher_factory.create_namespace(namespace.as_command_namespace())
        matcher = matcher_factory.empty_matcher()
        for stored_command in namespace.commands:
            command = GenericCommandProcessor().process(stored_command.syntax)
            matcher_factory.add_command(matcher, command, stored_command.name)

        normalized_matcher = normalize(matcher)
        normalized_namespace_matcher = normalize(namespace_matcher)
        priority_assigner.assign_all(plugin_name, normalized_matcher)

        namespace_component = NamespaceComponent(namespace.name,
                                                 normalized_namespace_matcher,
                                                 normalized_matcher,
                                                 namespace.definition_set,
                                                 dynamic_rule_set)
        namespace_components.append(namespace_component)

    return PluginStructure(plugin_name, namespace_components)




