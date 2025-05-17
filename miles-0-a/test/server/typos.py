from src.server.typos import compare_words


def test_typos():
    assert round(compare_words('insert', 'insetr')) == 67