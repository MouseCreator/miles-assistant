import pytest

from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from src.server.canvas_context import RequestContext
from src.server.canvas_grammar import canvas_grammar


def test_typos_in_command():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    matching_core.recognize_and_execute('insetr sqaure at 100 100', 'canvas', context)


def test_wrong_word():
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    with pytest.raises(RecognizerError) as exc_info:
        matching_core.recognize_and_execute('Add pink square  add 100 100', 'canvas', context)
