from src.miles.core.command.command import RootComponent, SequenceComponent, WordComponent
from src.miles.core.formatter.prints import print_matcher
from src.miles.core.matcher.matcher import MatcherFactory
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

