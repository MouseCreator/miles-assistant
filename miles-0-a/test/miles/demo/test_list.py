
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure, NodeType
from src.miles.shared.executor.executor_utils import CommandStructureSearch
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.collector import PluginCollector
from src.miles.shared.context_analyzer import AnyWordContextAnalyzer, WordContextAnalyzer
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext


class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        search = CommandStructureSearch(command_structure.get_root())
        names = search.find_matching("someone")
        size = len(names)
        message = f"Number of names: {size}"
        context.set(message)

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("hello", "Hello")
        namespace_init = plugin_register.add_namespace("list", "list")

        namespace_init.add_command("command1", "(HI, HELLO) someone [comma someone]", Command1Executor())

        namespace_init.add_matching("someone", AnyWordContextAnalyzer())
        namespace_init.add_matching("comma", WordContextAnalyzer(','))



def test_list():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()
    output_context = OutputContext()
    matching_core.recognize_and_execute('hello Michael, Daria, Eugene', namespace='list', context=output_context)

    assert output_context.get() == "Number of names: 3"