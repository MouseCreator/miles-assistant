import pytest

from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.shared.collector import PluginCollector
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext

class MockCommandExecutor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set('A')

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("letters")
        namespace_init = plugin_register.add_namespace("letters", "n s p")

        namespace_init.add_command("c1", "A B C D E", MockCommandExecutor())


def test_choice():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    output_context = OutputContext()

    with pytest.raises(RecognizerError) as exc_info:
        matching_core.recognize_and_execute("a b c", namespace="letters", context=output_context)

    assert str(exc_info.value) == 'Unable to recognize command! Unexpected end of input.'

    with pytest.raises(RecognizerError) as exc_info:
        matching_core.recognize_and_execute("a b c Y e", namespace="letters", context=output_context)

    assert str(exc_info.value) == 'Unable to recognize command! Error at position 4: Y'

    with pytest.raises(RecognizerError) as exc_info:
        matching_core.recognize_and_execute("n s a b c d e", context=output_context)

    assert str(exc_info.value) == 'Unable to recognize namespace! Error at position 3: a'