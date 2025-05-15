from src.miles.core.context.text_recognize_context import TextRecognizeContext
from src.miles.core.plugin.pipeline import create_normalized_matcher_from_definitions
from src.miles.core.plugin.plugin_definition import PluginDefinition, NamespaceOfCommands, StoredCommand
from src.miles.core.plugin.register_to_definitions import map_register_to_definition
from src.miles.core.recognizer.normalized_text_recognizer import recognize_extended
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.register import MilesRegister


class _MockExecutor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context):
        raise ValueError(f'Unexpected to call executor for temporary command')


class ExtendedCore:
    def __init__(self, plugin: str, namespace: str):
            reg = MilesRegister()
            plugins = map_register_to_definition(reg)
            self._plugin = None
            self._namespace = None
            for p in plugins:
                if p.name() == plugin:
                    self._plugin = p

            for n in self._plugin.namespaces():
                if n.name == namespace:
                    self._namespace = n

    def recognize_extended(self, context: TextRecognizeContext, command: str, name: str|None=None) -> CommandStructure | None:
        position = context.position()
        if name is None:
            name = 'target'
        stored_command = StoredCommand(name, command, _MockExecutor())
        namespace = NamespaceOfCommands(name='$_$',
                            prefix=None,
                            commands=[stored_command],
                            priority_manager=self._namespace.priority_manager,
                            dynamic_priorities=self._namespace.dynamic_priorities,
                            definition_set=self._namespace.definition_set,
                            word_analyzer_factory=self._namespace.word_analyzer_factory)
        temp_plugin = PluginDefinition(name='$_$', namespaces=[namespace])
        temp_plugin_structure = create_normalized_matcher_from_definitions(temp_plugin)
        ns = temp_plugin_structure.namespaces[0]
        return recognize_extended(context.all_tokens(), ns, position)
