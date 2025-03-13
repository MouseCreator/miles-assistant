from src.miles.core.matcher.matcher import MatchConnection, ConnectionType
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet, MatchingDefinition, MatchingStrategy
from src.miles.core.recognizer.text_recognizer import _TRReader
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

def test_keep_matching():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.MATCHING, 'plugin', 'h_rule')),
        (1, 2, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'WORLD')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'recognize COMMAND'))
    ]
    matcher = create_simple_matcher(matcher_origin)
    text = 'hello hi hola world'
    definition_set = MatchingDefinitionSet()

    def starts_with_h(word: str):
        return word.startswith('h')

    h_rule = MatchingDefinition(starts_with_h, 'plugin', 'h_rule', MatchingStrategy.KEEP_MATCHING)
    definition_set.append_definition(h_rule)

    r = _TRReader(matcher, text, definition_set)
    reached = r.recognize()
    assert len(reached) == 1
