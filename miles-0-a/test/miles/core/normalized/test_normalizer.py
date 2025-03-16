from src.miles.core.matcher.matcher import MatchConnection, ConnectionType
from src.miles.core.normalized.matcher_normalizer import _get_normalized_collection
from src.miles.utils.string_builder import lines
from test.miles.core.recognizer.simple_matcher_factory import create_simple_matcher


def test_normalizer_two_auto_ways():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'a')),
        (0, 2, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'b')),
        (1, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'c')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'd')),
    ]
    matcher = create_simple_matcher(matcher_origin)
    n = _get_normalized_collection(matcher)
    assert (
            lines(
                ["0 ->",
                 "ac -- 101",
                 "bd -- 101"]
            ) == n.sprint()
    )

def test_normalizer_two_ways():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'a')),
        (0, 2, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'b')),
        (1, 101, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'c')),
        (2, 101, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'd')),
    ]
    matcher = create_simple_matcher(matcher_origin)
    n = _get_normalized_collection(matcher)
    assert (
            lines(
                ["0 ->",
                 "ac -- 101",
                 "bd -- 101"]
            ) == n.sprint()
    )

def test_normalizer_loop():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'a')),
        (1, 0, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'b')),
        (1, 101, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'c')),
    ]
    matcher = create_simple_matcher(matcher_origin)
    n = _get_normalized_collection(matcher)
    assert (
            lines(
                ["0 ->",
                 "a -- 1",
                 "1 ->",
                 "ba -- 1",
                 "c -- 101"]
            ) == n.sprint())

def test_normalizer_empty_loop():
    matcher_origin = [
        (0, 1, 0, MatchConnection(ConnectionType.WORD, 'plugin', 'a')),
        (1, 2, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'b')),
        (2, 1, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'c')),
        (2, 0, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'd')),
        (2, 101, 0, MatchConnection(ConnectionType.AUTOMATIC, 'plugin', 'e')),
    ]
    matcher = create_simple_matcher(matcher_origin)
    n = _get_normalized_collection(matcher)
    assert (
    lines(
        ["0 ->",
        "a -- 1",
        "1 ->",
        "bda -- 1",
        "be -- 101"]
    ) == n.sprint() )