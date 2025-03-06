from src.miles.core.command.generic_command_processor import GenericCommandProcessor


def test_process_single_word():
    """
    Check if command processor is able to read a single reserved word
    """
    g = GenericCommandProcessor()
    command = g.process('HELLO')
    print()
    print(command)


def test_process_multiple_words():
    """
    Check if command processor is able to read a sequence of reserved words
    """
    g = GenericCommandProcessor()
    command = g.process('WELCOME TO THE WORLD')
    print()
    print(command)