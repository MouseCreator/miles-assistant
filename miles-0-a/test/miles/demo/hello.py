from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.executor.executor_utils import CommandStructureSearch
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.collector import PluginCollector
from src.miles.shared.context_analyzer import AnyWordContextAnalyzer, DefaultWordContextAnalyzerFactory
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext


class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set("Hi world!")

class Command2Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set("Hello world!")

class Command3Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        name = CommandStructureSearch(command_structure.get_root()).find_matching("name")[0].any()
        context.set(f"Hey {name}!")

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("hello", "Hello")
        namespace_init = plugin_register.add_namespace("hello", "h")

        namespace_init.add_command("command1", "HI", Command1Executor())
        namespace_init.add_command("command2", "HELLO", Command2Executor())
        namespace_init.add_command("command3", "(HI, HELLO) name", Command3Executor())

        namespace_init.add_matching("name", AnyWordContextAnalyzer())
        namespace_init.set_word_analyzer_factory(DefaultWordContextAnalyzerFactory())


def test_hello():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()
    output_context = OutputContext()
    matching_core.recognize_and_execute("h hi", context=output_context)
    assert output_context.get() == "Hi world!"

    matching_core.recognize_and_execute("h hello", context=output_context)
    assert output_context.get() == "Hello world!"

    matching_core.recognize_and_execute("h hi Michael", context=output_context)
    assert output_context.get() == "Hey Michael!"

    matching_core.recognize_and_execute("hello Michael", namespace="hello", context=output_context)
    assert output_context.get() == "Hey Michael!"