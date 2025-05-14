from typing import Any

from src.miles.core.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.context_analyzer import DefaultWordContextAnalyzerFactory, TypedContextAnalyzer
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure
from src.miles.shared.executor.executor_utils import CommandStructureSearch
from src.miles.shared.register import PluginRegister
from src.server.canvas_context import RequestContext


SHAPES = ['arrow', 'circle', 'square', 'triangle', 'hexagon', 'oval', 'line']
COLORS = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'violet', 'pink', 'brown']


def is_number(text: str):
    for char in text:
        if char < '0' or char > '9':
            return False
    return len(text) > 0

class AddCommandExecutor(CommandExecutor):
    def on_recognize(self, command_structure: CommandStructure, request_context: Any):
        pass

class ColorContextAnalyzer(TypedContextAnalyzer):
    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        if current_word in COLORS:
            context.consume()
        else:
            context.fail()

class ShapeContextAnalyzer(TypedContextAnalyzer):
    def invoke(self, context: TextRecognizeContext):
        current_word = context.current().lower()
        if current_word in SHAPES:
            context.consume()
        else:
            context.fail()

class NumberContextAnalyzer(TypedContextAnalyzer):
    def invoke(self, context: TextRecognizeContext):
        current_word = context.current()
        if is_number(current_word):
            context.consume()
        else:
            context.fail()

class CoordinatesContextAnalyzer(TypedContextAnalyzer):
    def invoke(self, context: TextRecognizeContext):
        for i in range(2):
            current_word = context.current()
            if is_number(current_word):
                context.consume()
            else:
                context.fail()

class SetterCommandExecutor(CommandExecutor):
    def __init__(self, setter_for: str):
        self.setter_for = setter_for

    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        identifier = int(search.find_ith(2).any())

        shapes = context.shapes()
        target = shapes.get_by_id(identifier)

        if self.setter_for == 'color':
            target.color = search.find_ith(4).any()
        elif self.setter_for == 'coord':
            val = search.find_ith(4).value()
            target.x = int(val[0])
            target.y = int(val[1])
        elif self.setter_for == 'x':
            target.x = int(search.find_ith(4).any())
        elif self.setter_for == 'y':
            target.y = int(search.find_ith(4).any())
        elif self.setter_for == 'shape':
            target.category = search.find_ith(4).any()
        elif self.setter_for == 'angle':
            target.category = int(search.find_ith(4).any())

class MoveCommandExecutor(CommandExecutor):
    def __init__(self):
        pass
    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        identifier = int(search.find_ith(2).any())

        shapes = context.shapes()
        target = shapes.get_by_id(identifier)
        val = search.find_ith(4).value()
        target.x = int(val[0])
        target.y = int(val[1])

class DeleteCommandExecutor(CommandExecutor):
    def __init__(self):
        pass
    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        search = CommandStructureSearch(command_structure.get_root())
        target = int(search.find_matching('number')[0].any())
        context.shapes().remove_by_id(target)

class ClearCommandExecutor(CommandExecutor):
    def __init__(self):
        pass
    def on_recognize(self, command_structure: CommandStructure, context: RequestContext):
        context.shapes().clear()


def canvas_grammar(plugin_register: PluginRegister):
    namespace_init = plugin_register.add_namespace("canvas", "canvas")

    namespace_init.add_command("add", "ADD { color } shape AT coordinates", AddCommandExecutor())
    namespace_init.add_command("set_color", "SET number COLOR color", SetterCommandExecutor('color'))
    namespace_init.add_command("set_coord", "SET number COORDINATES coordinates", SetterCommandExecutor('coord'))
    namespace_init.add_command("set_x", "SET number X number", SetterCommandExecutor('x'))
    namespace_init.add_command("set_y", "SET number Y number", SetterCommandExecutor('y'))
    namespace_init.add_command("set_shape", "SET number SHAPE shape", SetterCommandExecutor('shape'))
    namespace_init.add_command("set_angle", "SET number ANGLE number", SetterCommandExecutor('angle'))
    namespace_init.add_command("move", "MOVE number TO coordinates", MoveCommandExecutor())
    namespace_init.add_command("delete", "(DELETE, REMOVE) number", DeleteCommandExecutor())
    namespace_init.add_command("clear", "CLEAR { ALL }", ClearCommandExecutor())

    namespace_init.add_matching("color", ColorContextAnalyzer())
    namespace_init.add_matching("shape", ShapeContextAnalyzer())
    namespace_init.add_matching("coordinates", CoordinatesContextAnalyzer())
    namespace_init.add_matching("id", CoordinatesContextAnalyzer())
    namespace_init.set_word_analyzer_factory(DefaultWordContextAnalyzerFactory())