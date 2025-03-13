from src.miles.core.matcher.matcher import MatchConnection, ConnectionType
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.recognizer.text_recognizer import TextRecognizer
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

    r = TextRecognizer(matcher, text, definition_set)
    r.recognize()