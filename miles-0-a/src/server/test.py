from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from src.server.canvas_context import RequestContext
from src.server.canvas_grammar import canvas_grammar


if __name__ == '__main__':
    plugin = MilesRegister().create_plugin_register('app')
    canvas_grammar(plugin)
    matching_core = create_matching_core()
    context = RequestContext([], 0)
    matching_core.recognize_and_execute('add square at 100 100', 'canvas', context)
    matching_core.recognize_and_execute('set 1 color blue', 'canvas', context)
    matching_core.recognize_and_execute('move 1 to 500 500', 'canvas', context)
    matching_core.recognize_and_execute('remove 1', 'canvas', context)
