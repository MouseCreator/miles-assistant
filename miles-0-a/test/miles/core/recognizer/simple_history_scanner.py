from src.miles.core.recognizer.text_recognizer import _Pointer


def scan_history(reached_pointer: _Pointer):
    reached_pointer.get_history()
