from src.miles.core.command.generic_command_processor import GenericCommandProcessor


def test_process_single_word():
    """
    Check if command executor is able to read a single reserved word
    """
    g = GenericCommandProcessor()
    command = g.process('HELLO')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:HELLO)))'


def test_process_multiple_words():
    """
    Check if command executor is able to read a sequence of reserved words
    """
    g = GenericCommandProcessor()
    command = g.process('WELCOME TO THE WORLD')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:WELCOME),(WORD:TO),(WORD:THE),(WORD:WORLD)))'

def test_process_matching():
    """
    Check if command executor is able to read a matching placeholder
    """
    g = GenericCommandProcessor()
    command = g.process('placeholder')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(MATCHING:placeholder)))'

def test_process_matching_special_names():
    """
    Check if command executor is able to read a matching placeholder
    """
    g = GenericCommandProcessor()
    command = g.process('a_b _1 cd2')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(MATCHING:a_b),(MATCHING:_1),(MATCHING:cd2)))'

def test_process_multiple_matching():
    """
    Check if command executor is able to read a series of placeholders
    """
    g = GenericCommandProcessor()
    command = g.process('a b c')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(MATCHING:a),(MATCHING:b),(MATCHING:c)))'

def test_process_multiple_words_and_matching():
    """
    Check if command executor is able to read text with placeholders
    """
    g = GenericCommandProcessor()
    command = g.process('DISPLAY text WITH FONT font')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:DISPLAY),(MATCHING:text),(WORD:WITH),(WORD:FONT),(MATCHING:font)))'

def test_process_optional():
    """
    Check if command executor is able to read optional parameters
    """
    g = GenericCommandProcessor()
    command = g.process('{THIS IS OPTIONAL}')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(OPTIONAL:(SEQUENCE:(WORD:THIS),(WORD:IS),(WORD:OPTIONAL)))))'

def test_process_optional_in_context():
    """
    Check if command executor is able to recognize optional among other tokens
    """
    g = GenericCommandProcessor()
    command = g.process('A { B } C')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:A),(OPTIONAL:(SEQUENCE:(WORD:B))),(WORD:C)))'


def test_process_list():
    """
    Check if command executor is able to read list parameters
    """
    g = GenericCommandProcessor()
    command = g.process('[DO action]')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(LIST:(SEQUENCE:(WORD:DO),(MATCHING:action)))))'

def test_process_list_in_context():
    """
    Check if command executor is able to recognize list among other tokens
    """
    g = GenericCommandProcessor()
    command = g.process('action [AND action]')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(MATCHING:action),(LIST:(SEQUENCE:(WORD:AND),(MATCHING:action)))))'


def test_process_choice():
    """
    Check if command executor is able to read choice parameters
    """
    g = GenericCommandProcessor()
    command = g.process('(A, B, C)')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(CHOICE:(SEQUENCE:(WORD:A)),(SEQUENCE:(WORD:B)),(SEQUENCE:(WORD:C)))))'

def test_process_choice_in_context():
    """
    Check if command executor is able to recognize choice among other tokens
    """
    g = GenericCommandProcessor()
    command = g.process('SELECT (one two, three)')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:SELECT),(CHOICE:(SEQUENCE:(MATCHING:one),(MATCHING:two)),(SEQUENCE:(MATCHING:three)))))'

def test_combination():
    """
    Check if command executor can handle nesting of different parameters
    """
    g = GenericCommandProcessor()
    command = g.process("DO c {[AND (a, b)]}")
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:DO),(MATCHING:c),(OPTIONAL:(SEQUENCE:(LIST:(SEQUENCE:(WORD:AND),(CHOICE:(SEQUENCE:(MATCHING:a)),(SEQUENCE:(MATCHING:b)))))))))'


def test_named_arg():
    """
    Check if command executor can handle nesting of different parameters
    """
    g = GenericCommandProcessor()
    command = g.process("a=[NAMED LIST]")
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(a=(LIST:(SEQUENCE:(WORD:NAMED),(WORD:LIST))))))'
