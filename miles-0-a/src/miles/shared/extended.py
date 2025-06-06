from typing import List, Tuple

from src.miles.core.plugin.pipeline import create_normalized_matcher_from_definitions
from src.miles.core.plugin.plugin_definition import PluginDefinition, NamespaceOfCommands, StoredCommand
from src.miles.core.plugin.register_to_definitions import map_register_to_definition
from src.miles.core.recognizer.normalized_text_recognizer import recognize_extended
from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.register import MilesRegister
from src.miles.utils.strings import print_list


class _MockExecutor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context):
        raise ValueError(f'Unexpected to call executor for temporary command')


class ExtendedCore:
    def __init__(self, plugin: str, namespace: str, matching: str):
        self._plugin = plugin
        self._namespace = namespace
        self._matching = matching
        self._title = self._matching
        self._stored = []

    def init_commands(self, commands: List[Tuple[str, str]]):
        stored = []
        for c in commands:
            name = c[0]
            syntax = c[1]
            stored_command = StoredCommand(name, syntax, _MockExecutor())
            stored.append(stored_command)
        self._stored = stored

    def _select_namespace(self) -> NamespaceOfCommands:
        reg = MilesRegister()
        plugins = map_register_to_definition(reg)
        plugin = None
        for p in plugins:
            if p.name() == self._plugin:
                plugin = p
        if plugin is None:
            raise ValueError(f'Unknown plugin: {self._plugin}')
        for n in plugin.namespaces():
            if n.name == self._namespace:
                return n
        raise ValueError(f'Unknown namespace: {self._namespace}')

    def recognize_extended(self, context: TextRecognizeContext) -> List[CommandStructure]:
        selected = self._select_namespace()

        custom_namespace = NamespaceOfCommands(name=self._title,
                                               prefix=None,
                                               commands=self._stored,
                                               priority_manager=selected.priority_manager,
                                               dynamic_priorities=selected.dynamic_priorities,
                                               definition_set=selected.definition_set,
                                               word_analyzer_factory=selected.word_analyzer_factory,
                                               certainty_effect=selected.certainty_effect)
        position = context.position()
        if context.stack().contains(self._title, position):
            return []  # fails to avoid infinite loop

        temp_plugin = PluginDefinition(name=self._title, namespaces=[custom_namespace])
        temp_plugin_structure = create_normalized_matcher_from_definitions(temp_plugin)
        ns = temp_plugin_structure.namespaces[0]

        stack = context.stack().copy()
        stack.push(self._title, position)

        result = recognize_extended(self._title, context.all_tokens(), ns, position, stack, context.flags())

        return result


def single_variant(lst: List[CommandStructure]) -> CommandStructure | None:
    if len(lst) == 0:
        return None
    if len(lst) != 1:
        raise RecognizerError(f'Expected to have only one command structure, but got {len(lst)}: {print_list(lst)}')
    return lst[0]
