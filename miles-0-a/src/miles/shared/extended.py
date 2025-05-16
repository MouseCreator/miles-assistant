from typing import List, Tuple

from src.miles.shared.context.text_recognize_context import TextRecognizeContext
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
    def __init__(self, plugin: str, namespace: str, matching: str):
        self._plugin = plugin
        self._namespace = namespace
        self._matching = matching
        self._title = f'${self._matching}'
        self._stored = []

    def init_commands(self, commands: List[Tuple[str, str]]):
        stored = []
        for c in commands:
            name = c[0]
            syntax = c[1]
            stored_command = StoredCommand(name, syntax, _MockExecutor())
            stored.append(stored_command)
        self._stored = stored



    def recognize_extended(self, context: TextRecognizeContext) -> CommandStructure | None:
        reg = MilesRegister()
        plugins = map_register_to_definition(reg)
        for p in plugins:
            if p.name() == self._plugin:
                self._plugin = p

        for n in self._plugin.namespaces():
            if n.name == self._namespace:
                self._namespace = n

        custom_namespace = NamespaceOfCommands(name=self._title,
                                                     prefix=None,
                                                     commands=self._stored,
                                                     priority_manager=self._namespace.priority_manager,
                                                     dynamic_priorities=self._namespace.dynamic_priorities,
                                                     definition_set=self._namespace.definition_set,
                                                     word_analyzer_factory=self._namespace.word_analyzer_factory,
                                                     certainty_effect=self._namespace.certainty_effect)
        position = context.position()
        if context.stack().contains(self._title, position):
            return None # fails to avoid infinite loop

        temp_plugin = PluginDefinition(name=self._title, namespaces=[custom_namespace])
        temp_plugin_structure = create_normalized_matcher_from_definitions(temp_plugin)
        ns = temp_plugin_structure.namespaces[0]

        stack = context.stack().copy()
        stack.push(self._title, position)

        flags = context.flags().copy()

        result = recognize_extended(self._title, context.all_tokens(), ns, position, stack, context.flags())

        if result is not None:
            context.set_flags(flags)

        return result
