from src.miles.core.core_context import CoreContext
from src.miles.core.executor.command_executor import CommandExecutor
from src.miles.core.executor.command_structure import CommandStructure
from src.miles.core.matching_core import MatchingCore
from src.miles.core.matching_core_factory import create_matching_core
from src.miles.core.plugin.collector import PluginCollector
from src.miles.core.recognizer.context_analyzer import AnyWordContextAnalyzer, WordContextAnalyzer
from src.miles.core.register.register import MilesRegister

class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, core_context: CoreContext):
        print("Command 1 recognized!")

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("hello", "Hello")
        namespace_init = plugin_register.add_namespace("list", "list")

        namespace_init.add_command("command1", "(HI, HELLO) someone [comma someone]", Command1Executor())

        namespace_init.add_matching("someone", AnyWordContextAnalyzer())
        namespace_init.add_matching("comma", WordContextAnalyzer(','))



def do_test():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    matching_core.recognize_and_execute('hello Michael, Daria, Eugene', namespace='list')

if __name__ == '__main__':
    do_test()