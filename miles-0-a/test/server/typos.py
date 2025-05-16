from src.server.typos import TypoManager


def test_typos():
    tm = TypoManager()
    assert round(tm.compare_words('insert', 'insetr')) == 67