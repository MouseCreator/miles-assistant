from src.miles.core.command.command import RootComponent, SequenceComponent, WordComponent
from src.miles.core.formatter.prints import print_matcher
from src.miles.core.matcher.matcher import MatcherFactory
from src.miles.utils.string_builder import lines
from test.miles.core.matcher.simple_pool_factory import SimpleCommandPoolFactory


def test_single_word():
    pool_factory = SimpleCommandPoolFactory()
    pool_factory.append(RootComponent(
        content=SequenceComponent(
            sequence=[
                WordComponent('PRINT')
            ]
        )
    ),
        namespace=None,
        plugin='plugin',
        command_name='print'
    )
    pool = pool_factory.get()
    matcher_factory = MatcherFactory(pool)
    matcher = matcher_factory.create()
    expected = " [] ---(WORD, plugin, PRINT)--> [] ---(AUTOMATIC, plugin, recognize plugin||print)--> [] "
    actual = print_matcher(matcher)
    assert expected == actual


def test_two_single_word_commands():
    pool_factory = SimpleCommandPoolFactory()
    pool_factory.append(RootComponent(
        content=SequenceComponent(
            sequence=[
                WordComponent('PRINT')
            ]
        )
    ),
        namespace=None,
        plugin='plugin',
        command_name='print'
    )
    pool_factory.append(RootComponent(
        content=SequenceComponent(
            sequence=[
                WordComponent('WRITE')
            ]
        )
    ),
        namespace=None,
        plugin='plugin',
        command_name='write'
    )
    pool = pool_factory.get()
    matcher_factory = MatcherFactory(pool)
    matcher = matcher_factory.create()
    expected = lines([
        " [] ---(WORD, plugin, PRINT)--> [] ---(AUTOMATIC, plugin, recognize plugin||print)--> [] ",
        "    ---(WORD, plugin, WRITE)--> [] ---(AUTOMATIC, plugin, recognize plugin||write)--> [] "
    ]
    )
    actual = print_matcher(matcher)
    print()
    print(actual)
    assert expected == actual

