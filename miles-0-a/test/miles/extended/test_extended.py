from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.extended import ExtendedCore
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.collector import PluginCollector
from src.miles.shared.context_analyzer import TypedContextAnalyzer
from src.miles.shared.register import MilesRegister
from test.miles.demo.output_context import OutputContext


class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set('pair')

class Command2Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        context.set('recursion')


class PairAnalyzer(TypedContextAnalyzer):

    def __init__(self):
        commands = [
            ('c1', 'A B'),
            ('c2', 'C D'),
            ('c3', 'E F'),
        ]
        self._core = ExtendedCore(plugin='extended', namespace='extended', matching='pair')
        self._core.init_commands(commands)

    def invoke(self, context: TextRecognizeContext):
        structures = self._core.recognize_extended(context=context)
        if not structures:
            context.fail()
            return

        for s in structures:
            context.variant(s.size())

class RecursionAnalyzer(TypedContextAnalyzer):

    def __init__(self):
        commands = [
            ('c1', 'Z recursion'),
            ('c2', 'Y recursion'),
            ('c3', 'Z'),
            ('c4', 'Y'),
        ]
        self._core = ExtendedCore(plugin='extended', namespace='extended', matching='recursion')
        self._core.init_commands(commands)

    def invoke(self, context: TextRecognizeContext):
        structures = self._core.recognize_extended(context=context)
        if not structures:
            context.fail()
            return
        for s in structures:
            context.variant(s.size())


class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register('extended')
        namespace_init = plugin_register.add_namespace('extended', 'extended')

        namespace_init.add_command('command1', 'pair', Command1Executor())
        namespace_init.add_command('command2', 'recursion', Command2Executor())

        namespace_init.add_matching('pair', PairAnalyzer())
        namespace_init.add_matching('recursion', RecursionAnalyzer())


def test_extended():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()
    output_context = OutputContext()

    matching_core.recognize_and_execute('a b', context=output_context, namespace='extended')
    assert output_context.get() == 'pair'

    matching_core.recognize_and_execute('c d', context=output_context, namespace='extended')
    assert output_context.get() == 'pair'

    matching_core.recognize_and_execute('e f', context=output_context, namespace='extended')
    assert output_context.get() == 'pair'

    matching_core.recognize_and_execute('z', context=output_context, namespace='extended')
    assert output_context.get() == 'recursion'

    matching_core.recognize_and_execute('z z z', context=output_context, namespace='extended')
    assert output_context.get() == 'recursion'

    matching_core.recognize_and_execute('y y y', context=output_context, namespace='extended')
    assert output_context.get() == 'recursion'

    matching_core.recognize_and_execute('y z y z', context=output_context, namespace='extended')
    assert output_context.get() == 'recursion'