from src.miles.core.core_context import CoreContext
from src.miles.core.executor.command_executor import CommandExecutor
from src.miles.core.executor.command_structure import CommandStructure
from src.miles.core.executor.executor_utils import CommandStructureSearch
from src.miles.core.matching_core import MatchingCore
from src.miles.core.matching_core_factory import create_matching_core
from src.miles.core.plugin.collector import PluginCollector
from src.miles.core.recognizer.context_analyzer import AnyWordContextAnalyzer
from src.miles.core.register.register import MilesRegister


class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, core_context: CoreContext):
        print("Hi world!")

class Command2Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, core_context: CoreContext):
        print("Hello world!")

class Command3Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, core_context: CoreContext):
        name = CommandStructureSearch(command_structure.get_root()).find_matching("name")[0]
        print(f"Hello {name}")

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("hello", "Hello")
        namespace_init = plugin_register.add_namespace("hello", "h")

        namespace_init.add_command("command1", "HI", Command1Executor())
        namespace_init.add_command("command2", "HELLO", Command2Executor())
        namespace_init.add_command("command3", "(HI, HELLO) name", Command3Executor())

        namespace_init.add_matching("name", AnyWordContextAnalyzer())



def do_test():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    matching_core.recognize_and_execute("h hi")
    print("-------")

    matching_core.recognize_and_execute("h hello")
    print("-------")

    matching_core.recognize_and_execute("h hi Michael")
    print("-------")

    matching_core.recognize_and_execute("hello Michael", namespace="h")
    print("-------")

if __name__ == '__main__':
    do_test()