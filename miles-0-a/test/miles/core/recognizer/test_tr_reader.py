from src.miles.core.matcher.matcher import MatchConnection, ConnectionType
from src.miles.core.recognizer.context_analyzer import TypedContextAnalyzer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet, MatchingDefinition
from src.miles.core.recognizer.optimization import RecOptimizationStrategy
from src.miles.core.recognizer.priority import PriorityManager
from src.miles.core.data.recognize_context import RecognizeContext
from src.miles.core.recognizer.text_recognizer import _TRReader
from test.miles.core.recognizer.simple_history_scanner import scan_history
from test.miles.core.recognizer.simple_matcher_factory import create_simple_matcher


def test_word_sequence():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'HELLO')),
        (1, 2, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'WORLD')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = 'hello world'
    definition_set = MatchingDefinitionSet()

    r = _TRReader(matcher, text, definition_set)
    reached = r.recognize()
    assert reached is not None
    assert scan_history(text, reached[0]) == ['hello', 'world', '!recognize COMMAND']

def test_analyzer():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.MATCHING, 'plugin', 'h_rule')),
        (1, 2, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'WORLD')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = 'hello hi hola world'
    definition_set = MatchingDefinitionSet()

    class HAnalyzer(TypedContextAnalyzer):

        def invoke(self, context: RecognizeContext):
            while context.has_any():
                if context.current().startswith('h'):
                   context.consume()
                else:
                    break

    h_rule = MatchingDefinition(HAnalyzer(), 'plugin', 'h_rule')
    definition_set.append_definition(h_rule)

    r = _TRReader(matcher, text, definition_set)
    reached = r.recognize()
    assert reached is not None
    assert scan_history(text, reached) == ['hello hi hola', 'world', '!recognize COMMAND']

def test_loop():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'REPEAT')),
        (1, 0, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'loop back')),
        (1, 2, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'AGAIN')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = 'repeat repeat repeat again'
    definition_set = MatchingDefinitionSet()

    r = _TRReader(matcher, text, definition_set)
    reached = r.recognize()
    assert reached is not None
    assert scan_history(text, reached) == ['repeat', '!loop back',
                                              'repeat', '!loop back',
                                              'repeat', 'again',
                                              '!recognize COMMAND']


def test_shortest_first():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.MATCHING, 'plugin', 'text')),
        (1, 0, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'loop back')),
        (1, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = 'a b c d e'
    definition_set = MatchingDefinitionSet()

    class ShortestContextAnalyzer(TypedContextAnalyzer):
        def __init__(self):
            pass

        def invoke(self, context: RecognizeContext):
            while context.has_any():
                context.consume(interrupted=True)

        def optimization_strategy(self) -> RecOptimizationStrategy:
            return RecOptimizationStrategy.SHORTEST_FIRST
    text_rule = MatchingDefinition(ShortestContextAnalyzer(), 'plugin', 'text')
    definition_set.append_definition(text_rule)

    r = _TRReader(matcher, text, definition_set)
    reached = r.recognize()

    assert scan_history(text, reached) == ['a', '!loop back',
                                           'b', '!loop back',
                                           'c', '!loop back',
                                           'd', '!loop back',
                                           'e', '!recognize COMMAND']

def test_longest_first():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.MATCHING, 'plugin', 'text')),
        (1, 0, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'loop back')),
        (1, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = 'a b c d e'
    definition_set = MatchingDefinitionSet()

    class LongestContextAnalyzer(TypedContextAnalyzer):
        def __init__(self):
            pass

        def invoke(self, context: RecognizeContext):
            while context.has_any():
                context.consume(interrupted=True)

        def optimization_strategy(self) -> RecOptimizationStrategy:
            return RecOptimizationStrategy.SHORTEST_FIRST
    text_rule = MatchingDefinition(LongestContextAnalyzer(), 'plugin', 'text')
    definition_set.append_definition(text_rule)

    r = _TRReader(matcher, text, definition_set)
    reached = r.recognize()

    assert scan_history(text, reached) == ['a b c d e', '!recognize COMMAND']


def test_priorities():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'path 1')),
        (0, 2, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'path 2')),
        (0, 3, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'path 3')),
        (1, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND')),
        (3, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = ''
    priority_manager = PriorityManager()
    priority_manager.set_priority('plugin', ConnectionType.AUTOMATIC, 'path 1', 1000)
    priority_manager.set_priority('plugin', ConnectionType.AUTOMATIC, 'path 2', 1001)
    priority_manager.set_priority('plugin', ConnectionType.AUTOMATIC, 'path 3', 1002)

    r = _TRReader(matcher, text, priority_manager=priority_manager)
    reached = r.recognize()

    assert reached is not None
    assert scan_history(text, reached) == ['!path 3', '!recognize COMMAND']
