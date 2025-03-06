from src.miles.core.command.generic_command_processor import GenericCommandProcessor


def test_process_single_word():
    """
    Check if command processor is able to read a single reserved word
    """
    g = GenericCommandProcessor()
    command = g.process('HELLO')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:HELLO)))'


def test_process_multiple_words():
    """
    Check if command processor is able to read a sequence of reserved words
    """
    g = GenericCommandProcessor()
    command = g.process('WELCOME TO THE WORLD')
    assert str(command) == 'Command: (ROOT:(SEQUENCE:(WORD:WELCOME),(WORD:TO),(WORD:THE),(WORD:WORLD)))'