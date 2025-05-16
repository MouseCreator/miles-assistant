from src.miles.shared.collector import PluginCollector
from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.context_analyzer import TypedContextAnalyzer
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext

class OneCommandExecutor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set('one')

class TwoCommandExecutor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set('two')

class OneAnalyzer(TypedContextAnalyzer):

    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        if current_word == 'one':
            context.consume(certainty=70)
        elif current_word == 'two':
            context.consume(certainty=30)
        else:
            context.fail()

class TwoAnalyzer(TypedContextAnalyzer):

    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        if current_word == 'one':
            context.consume(certainty=30)
        elif current_word == 'two':
            context.consume(certainty=70)
        else:
            context.fail()

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("numbers")
        namespace_init = plugin_register.add_namespace("numbers", "numbers")

        namespace_init.add_command("c1", "one", OneCommandExecutor())
        namespace_init.add_command("c2", "two", TwoCommandExecutor())
        namespace_init.add_matching('one', OneAnalyzer())
        namespace_init.add_matching('two', TwoAnalyzer())

def test_certainty():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    output_context = OutputContext()

    matching_core.recognize_and_execute("one", namespace="numbers", context=output_context)
    assert output_context.get() == "one"

    matching_core.recognize_and_execute("two", namespace="numbers", context=output_context)
    assert output_context.get() == "two"

