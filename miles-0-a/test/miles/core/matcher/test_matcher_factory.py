from src.miles.core.command.command import RootComponent, SequenceComponent, WordComponent, ListComponent
from src.miles.core.formatter.prints import print_matcher
from src.miles.core.matcher.matcher_factory import MatcherFactory
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


def test_list_of_words():
    pool_factory = SimpleCommandPoolFactory()
    pool_factory.append(RootComponent(
        content=SequenceComponent(
            sequence=[
                ListComponent(
                    content=SequenceComponent(
                        sequence=[
                            WordComponent('REPEAT')
                        ]
                    )
                )
            ]
        )
    ),
        namespace=None,
        plugin='plugin',
        command_name='repeat'
    )
    pool = pool_factory.get()
    matcher_factory = MatcherFactory(pool)
    matcher = matcher_factory.create()
    expected = lines([
        ' [] ---(AUTOMATIC, plugin, begin list)--> [] ---(WORD, plugin, REPEAT)--> [] ---(AUTOMATIC, plugin, repeat list)--> [1] ',
        '                                                                             ---(AUTOMATIC, plugin, end list)--> [] ',
        '                                                                             ---(AUTOMATIC, plugin, recognize plugin||repeat)--> [] '
    ]
    )
    actual = print_matcher(matcher)
    print(actual)
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
    assert expected == actual

def test_same_prefix():
    pool_factory = SimpleCommandPoolFactory()
    pool_factory.append(RootComponent(
        content=SequenceComponent(
            sequence=[
                WordComponent('PRINT'),
                WordComponent('HELLO')
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
                WordComponent('PRINT'),
                WordComponent('BYE')
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
        " [] ---(WORD, plugin, PRINT)--> [] ---(WORD, plugin, HELLO)--> [] ---(AUTOMATIC, plugin, recognize plugin||print)--> [] ",
        "                                   ---(WORD, plugin, BYE)--> [] ---(AUTOMATIC, plugin, recognize plugin||write)--> [] "
    ]
    )
    actual = print_matcher(matcher)
    assert expected == actual

