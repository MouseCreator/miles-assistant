from src.miles.shared.collector import PluginCollector
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure, NodeType
from src.miles.shared.executor.executor_utils import CommandStructureSearch
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext


class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        search = CommandStructureSearch(command_structure.get_root())
        choice_item = search.find_by_type(NodeType.CHOICE)[0]
        text = choice_item.children()[0].any()
        context.set(f"{text} e")

class Command2Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set("C D E")

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("letters")
        namespace_init = plugin_register.add_namespace("letters", "h")

        namespace_init.add_command("abe", "(A, B) E", Command1Executor())
        namespace_init.add_command("cde", "(C, D) E", Command2Executor())


def test_choice():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    output_context = OutputContext()

    matching_core.recognize_and_execute("a e", namespace="letters", context=output_context)
    assert output_context.get() == "a e"

    matching_core.recognize_and_execute("b e", namespace="letters", context=output_context)
    assert output_context.get() == "b e"

    matching_core.recognize_and_execute("c e", namespace="letters", context=output_context)
    assert output_context.get() == "c e"

    matching_core.recognize_and_execute("d e", namespace="letters", context=output_context)
    assert output_context.get() == "d e"