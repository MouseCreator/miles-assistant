from src.miles.shared.collector import PluginCollector
from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.context_analyzer import WordContextAnalyzerFactory, TypedContextAnalyzer
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.priority.dynamic_priority import DynamicPriorityRule, DynamicPriorityContext
from src.miles.shared.priority.priority_rule import GeneralMatchingRule
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext


class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set("command 1")

class Command2Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set("command 2")

class WordPriorityRule(DynamicPriorityRule):

    def is_applicable(self, context: DynamicPriorityContext) -> bool:
        return context.is_word()

    def priority(self, context: DynamicPriorityContext) -> int:
        next_word = context.current()
        expected_word = context.argument()
        return 50 - abs(len(next_word) - len(expected_word))

class MonthPriorityRule(DynamicPriorityRule):

    def is_applicable(self, context: DynamicPriorityContext) -> bool:
        return context.is_matching() and context.argument().lower() == 'month'

    def priority(self, context: DynamicPriorityContext) -> int:

        current_word = context.current().lower()

        if current_word in ['december', 'january', 'february',
                            'march', 'april', 'may',
                            'june', 'july', 'august',
                            'september', 'october', 'november']:
            return 40

        return context.static_priority()

class MonthAnalyzer(TypedContextAnalyzer):

    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        if current_word in ['december', 'january', 'february',
                            'march', 'april', 'may',
                            'june', 'july', 'august',
                            'september', 'october', 'november']:
            context.consume()
        else:
            context.fail()


class WordTypoAnalyzer(TypedContextAnalyzer):
    def __init__(self, word: str):
        self.word = word

    def invoke(self, context: TextRecognizeContext):
        current = context.current()
        if len(current) == len(self.word):
            context.consume()
        else:
            context.fail()

class TypoWordContextAnalyzerFactory(WordContextAnalyzerFactory):

    def build(self, word: str) -> TypedContextAnalyzer:
        return WordTypoAnalyzer(word)



class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("year")
        namespace_init = plugin_register.add_namespace("year", "year")

        namespace_init.add_command("c1", "I LOVE JANUARY", Command1Executor())
        namespace_init.add_command("c2", "I LOVE month", Command2Executor())
        namespace_init.add_static_priority_rule(GeneralMatchingRule(20))
        namespace_init.add_dynamic_priority_rule(MonthPriorityRule())
        namespace_init.add_dynamic_priority_rule(WordPriorityRule())
        namespace_init.add_matching('month', MonthAnalyzer())
        namespace_init.set_word_analyzer_factory(TypoWordContextAnalyzerFactory())

def test_choice():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    output_context = OutputContext()

    matching_core.recognize_and_execute("a move january", namespace="year", context=output_context)
    assert output_context.get() == "command 1"

    matching_core.recognize_and_execute("a move february", namespace="year", context=output_context)
    assert output_context.get() == "command 2"