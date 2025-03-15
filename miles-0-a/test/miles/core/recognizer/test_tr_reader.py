from src.miles.core.matcher.matcher import MatchConnection, ConnectionType
from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet, MatchingDefinition
from src.miles.core.recognizer.recognize_context import RecognizeContext
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
    assert len(reached) == 1
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

    class HAnalyzer(GenericContextAnalyzer):

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
    assert len(reached) == 1
    assert scan_history(text, reached[0]) == ['hello hi hola', 'world', '!recognize COMMAND']
