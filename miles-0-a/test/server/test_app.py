from sympy.testing import pytest

from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.shared.context.flags import Flags
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from src.server.canvas_context import RequestContext
from src.server.canvas_grammar import canvas_grammar


def test_typos_in_command():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    flags = Flags()
    flags.set_flag('source', 'text')
    matching_core.recognize_and_execute('insetr sqaure at 100 100', 'canvas', context, flags)


def test_wrong_word():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    flags = Flags()
    flags.set_flag('source', 'audio')
    matching_core.recognize_and_execute('Add pink square  add 100 100', 'canvas', context, flags)

def test_correct_audio_command():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    flags = Flags()
    flags.set_flag('source', 'audio')
    matching_core.recognize_and_execute('Insert yellow square at 100 200', 'canvas', context, flags)
    assert context.shapes().size() == 1

def test_move_audio_command():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    flags = Flags()
    flags.set_flag('source', 'audio')
    matching_core.recognize_and_execute('Insert yellow square at 100 200', 'canvas', context, flags)
    matching_core.recognize_and_execute('Move A to coordinates 70 17', 'canvas', context, flags)
    assert context.shapes().size() == 1
    assert context.shapes().get_by_id('A').x == 70
    assert context.shapes().get_by_id('A').y == 17

def test_invalid_input():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    flags = Flags()
    flags.set_flag('source', 'text')
    with pytest.raises(RecognizerError) as exc_info:
        matching_core.recognize_and_execute('r', 'canvas', context, flags)
