from typing import List

from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.extended import ExtendedCore
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.collector import PluginCollector
from src.miles.shared.context_analyzer import TypedContextAnalyzer
from src.miles.shared.register import MilesRegister
from src.miles.utils.decorators import auto_str
from test.miles.demo.output_context import OutputContext


SCOPE = 'results'

@auto_str
class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

class Command1Executor(CommandExecutor):

    def on_recognize(self, command_structure: CommandStructure, context: OutputContext):
        t_res = command_structure.get_root()[1].result()
        num_students = len(t_res)
        context.set(f'{num_students}')

class AgeAnalyzer(TypedContextAnalyzer):

    def invoke(self, context: TextRecognizeContext):
        current = context.current()
        try:
            a = int(current)
            context.consume()
            context.set_result(a)
        except ValueError:
            context.fail()

class NameAnalyzer(TypedContextAnalyzer):

    def invoke(self, context: TextRecognizeContext):
        current = context.current()
        context.consume()
        context.set_result(current)

class StudentAnalyzer(TypedContextAnalyzer):

    def __init__(self):
        commands = [('st', 'name age')]
        self._core = ExtendedCore(plugin=SCOPE, namespace=SCOPE, matching='student')
        self._core.init_commands(commands)

    def invoke(self, context: TextRecognizeContext):
        structure = self._core.recognize_extended(context=context)
        if structure is None:
            context.fail()
            return
        context.consume(structure.size())
        root = structure.get_root()
        name = root[0].typed_result(str)
        age = root[1].typed_result(int)
        student = Student(name, age)
        context.set_result(student)

class StudentListAnalyzer(TypedContextAnalyzer):

    def __init__(self):
        commands = [
            ('one', 'student'),
            ('multi', 'student student_list')
        ]
        self._core = ExtendedCore(plugin=SCOPE, namespace=SCOPE, matching='student_list')
        self._core.init_commands(commands)

    def invoke(self, context: TextRecognizeContext):
        structure = self._core.recognize_extended(context=context)
        if structure is None:
            context.fail()
            return
        context.consume(structure.size())
        root = structure.get_root()
        if structure.get_command_name() == 'one':
            student = root.children()[0].result()
            context.set_result([student])
        else:
            prev_students = root.children()[1].typed_result(List)
            new_student = root.children()[0].typed_result(Student)
            prev_students.append(new_student)
            context.set_result(prev_students)

class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register(SCOPE)
        namespace_init = plugin_register.add_namespace(SCOPE, SCOPE)

        namespace_init.add_command('command1', 'STUDENTS student_list', Command1Executor())
        namespace_init.add_matching('age', AgeAnalyzer())
        namespace_init.add_matching('name', NameAnalyzer())
        namespace_init.add_matching('student', StudentAnalyzer())
        namespace_init.add_matching('student_list', StudentListAnalyzer())


def test_extended():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()
    output_context = OutputContext()

    matching_core.recognize_and_execute('students mike 20 emmy 18', context=output_context, namespace=SCOPE)
    assert output_context.get() == '2'