import random

from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.context_analyzer import TypedContextAnalyzer, \
    WordContextAnalyzerFactory
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure, NodeType
from src.miles.shared.executor.executor_utils import CommandStructureSearch
from src.miles.shared.extended import ExtendedCore, single_variant
from src.miles.shared.register import PluginRegister
from src.server.canvas_context import RequestContext, Shape
from src.server.shape_error import ShapeError
from src.server.typos import TypoManager

SHAPES = ['arrow', 'circle', 'square', 'triangle', 'hexagon', 'oval', 'line']
COLORS = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'violet', 'pink', 'brown']


def is_number(text: str):
    for char in text:
        if char < '0' or char > '9':
            return False
    return len(text) > 0


class TypoWordAnalyzer(TypedContextAnalyzer):

    def __init__(self, word: str):
        super().__init__()
        self.word = word.lower()
        self.typo_manager = TypoManager()

    def invoke(self, context: TextRecognizeContext):
        current = context.current().lower()
        word_comparison = self.typo_manager.compare_words(current, self.word)
        context.consume(certainty=word_comparison)

class TypoWordAnalyzerFactory(WordContextAnalyzerFactory):

    def build(self, word: str) -> TypedContextAnalyzer:
        return TypoWordAnalyzer(word)


class AddCommandExecutor(CommandExecutor):
    def on_recognize(self, command_structure: CommandStructure, request_context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        optional_color = search.find_by_type(NodeType.OPTIONAL)[0]
        if optional_color:
            color = optional_color.children()[0].any()
        else:
            color = random.choice(COLORS)
        shape = Shape(
            identity=request_context.new_identity(),
            category=search.find_matching('shape')[0].any(),
            x=int(search.find_matching('coordinates')[0].value()[0]),
            y=int(search.find_matching('coordinates')[0].value()[1]),
            color=color,
            angle=0
        )
        request_context.shapes().add(shape)

class ColorContextAnalyzer(TypedContextAnalyzer):
    def __init__(self):
        self._typos = TypoManager()
    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        certainty = self._typos.is_one_of(current_word, COLORS)
        context.consume(certainty=certainty)

class ShapeContextAnalyzer(TypedContextAnalyzer):
    def __init__(self):
        self._typos = TypoManager()
    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        certainty = self._typos.is_one_of(current_word, SHAPES)
        context.consume(certainty=certainty)

class NumberContextAnalyzer(TypedContextAnalyzer):
    def invoke(self, context: TextRecognizeContext):
        current_word = context.current()
        if is_number(current_word):
            context.consume()
        else:
            context.fail()

class CoordinatesContextAnalyzer(TypedContextAnalyzer):

    def __init__(self):
        self._core = ExtendedCore('app', 'canvas', 'coordinates')
        self._core.init_commands([
            ('simple', 'x=number {AND} y=number'),
            ('complex', 'X x=number {AND} Y y=number')
        ])

    def invoke(self, context: TextRecognizeContext):
        command_structures = self._core.recognize_extended(context=context)
        if not command_structures:
            context.fail()
        command_structure = single_variant(command_structures)
        search = CommandStructureSearch(command_structure.get_root())
        x = search.find_all_named('x')[0].any()
        y = search.find_all_named('y')[0].any()
        context.ignore(command_structure.get_root().size())
        context.write([x, y])


class SetterCommandExecutor(CommandExecutor):
    def __init__(self, setter_for: str):
        self.setter_for = setter_for

    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        identifier = int(search.find_ith(1).any())

        shapes = context.shapes()
        target = shapes.get_by_id(identifier)

        if target is None:
            raise ValueError(f'No shape with id {identifier} found!')
        setter = self.setter_for
        if setter == 'color':
            target.color = search.find_ith(3).any()
        elif setter == 'coord':
            val = search.find_ith(4).value()
            target.x = int(val[0])
            target.y = int(val[1])
        elif setter == 'x':
            target.x = int(search.find_ith(3).any())
        elif setter == 'y':
            target.y = int(search.find_ith(3).any())
        elif setter == 'shape':
            target.category = search.find_ith(3).any()
        elif setter == 'angle':
            target.angle = int(search.find_ith(3).any())
        else:
            raise ShapeError(f'Unknown setter method: {setter}')

class MoveCommandExecutor(CommandExecutor):
    def __init__(self):
        pass
    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        identifier = int(search.find_ith(1).any())

        shapes = context.shapes()
        target = shapes.get_by_id(identifier)
        if target is None:
            raise ShapeError(f'No shape with identifier {target}')
        val = search.find_ith(3).value()
        target.x = int(val[0])
        target.y = int(val[1])

class DeleteCommandExecutor(CommandExecutor):
    def __init__(self):
        pass
    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        target = int(search.find_matching('number')[0].any())

        has_target = False
        for shape in context.shapes():
            if shape.identity == target:
                has_target = True

        if not has_target:
            raise ShapeError(f'No shape with identifier {target}')

        context.shapes().remove_by_id(target)

class ClearCommandExecutor(CommandExecutor):
    def __init__(self):
        pass
    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        context.shapes().clear()
        context.clear_identity()


def canvas_grammar(plugin_register: PluginRegister):
    namespace_init = plugin_register.add_namespace("canvas", "canvas")

    namespace_init.add_command("add", "(ADD, DRAW, INSERT) { color } shape AT coordinates", AddCommandExecutor())
    namespace_init.add_command("set_color", "SET number COLOR color", SetterCommandExecutor('color'))
    namespace_init.add_command("set_coord", "SET number COORDINATES coordinates", SetterCommandExecutor('coord'))
    namespace_init.add_command("set_x", "SET number X number", SetterCommandExecutor('x'))
    namespace_init.add_command("set_y", "SET number Y number", SetterCommandExecutor('y'))
    namespace_init.add_command("set_shape", "SET number SHAPE shape", SetterCommandExecutor('shape'))
    namespace_init.add_command("set_angle", "SET number ANGLE number", SetterCommandExecutor('angle'))
    namespace_init.add_command("move", "MOVE number TO coordinates", MoveCommandExecutor())

    namespace_init.add_command("delete1", "(DELETE, REMOVE) number", DeleteCommandExecutor())
    namespace_init.add_command("clear", "CLEAR { ALL }", ClearCommandExecutor())

    namespace_init.add_matching("color", ColorContextAnalyzer())
    namespace_init.add_matching("shape", ShapeContextAnalyzer())
    namespace_init.add_matching("coordinates", CoordinatesContextAnalyzer())
    namespace_init.add_matching("number", NumberContextAnalyzer())
    namespace_init.set_word_analyzer_factory(TypoWordAnalyzerFactory())