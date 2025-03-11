
from xmlrpc.client import Error

from src.miles.core.command.command_processor_error import CommandProcessorError
from src.miles.core.command.command import Command, RootComponent, \
    WordComponent, MatchingComponent, ChoiceComponent, ListComponent, OptionalComponent, SequenceComponent, \
    NamedComponent
from src.miles.core.command.command_processor import CommandProcessor

from lark import Lark, Transformer

from src.miles.utils.singleton import Singleton

class _GenericCommandTransformer(Transformer):

    def _list_items(self, items):
        return ','.join(str(x) for x in items)

    def start(self, items):
        return items[0]
    def skip(self, items):
        return items[0]

    def sequence(self, items):
        return SequenceComponent(items)

    def root(self, items):
        if len(items) == 1:
            return RootComponent(items[0])
        raise CommandProcessorError(f'Invalid root component items: {self._list_items(items)}')

    def word(self, items):
        if len(items) != 1:
            raise CommandProcessorError(f'Unexpected items for WORD: {self._list_items(items)}')
        _word = items[0].value
        return WordComponent(_word)

    def matching(self, items):
        if len(items) != 1:
            raise CommandProcessorError(f'Unexpected items for WORD: {self._list_items(items)}')
        _mtch = items[0].value
        return MatchingComponent(_mtch)

    def choice(self, items):
        return ChoiceComponent(items)

    def list(self, items):
        return ListComponent(items)

    def optional(self, items):
        return OptionalComponent(items)

    def named(self, items):
        return NamedComponent(items[0].value, items[1])


class _GenericCommandParser(metaclass=Singleton):
    def __init__(self):
        grammar = r"""
            start:   sequence                   -> root
            sequence: expr+                     -> sequence
            expr: WORD                          -> word
                | MATCHING                      -> matching
                | MATCHING "=" expr             -> named
                | list                          -> skip
                | choice                        -> skip
                | optional                      -> skip
    
            choice: "(" sequence ("," sequence)* ")"    -> choice
            list: "[" sequence "]"                      -> list
            optional: "{" sequence "}"                  -> optional
            
            WORD: /[A-Z]+/
            MATCHING: /[a-z_][a-zA-Z0-9_]*/
    
            %import common.WS
            %ignore WS
        """

        self.content = Lark(grammar, start="start", parser="lalr")


class GenericCommandProcessor(CommandProcessor):
    def __init__(self, parser: Lark | None = None, transformer: Transformer | None = None):
        if parser is None:
            parser = _GenericCommandParser().content
        if transformer is None:
            transformer = _GenericCommandTransformer()
        self._parser = parser
        self._transformer = transformer

    def process(self, command_string: str) -> Command:
        try:
            tree = self._parser.parse(command_string)
            transformed = self._transformer.transform(tree)
            named_command = self._transformer.transform(transformed)
        except Error as e:
            raise CommandProcessorError('Command parsing error') from e
        if not isinstance(named_command, RootComponent):
            raise CommandProcessorError(f'Unexpected parsing output: ' + named_command)
        return Command(named_command)