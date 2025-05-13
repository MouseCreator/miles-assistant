
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.collector import PluginCollector
from src.miles.shared.context_analyzer import AnyWordContextAnalyzer, WordContextAnalyzer
from src.miles.shared.register import MilesRegister

class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure):
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