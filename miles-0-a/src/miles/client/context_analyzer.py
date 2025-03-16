from abc import ABC

from src.miles.core.recognizer.context_analyzer import TypedContextAnalyzer


class ClientContextAnalyzer(TypedContextAnalyzer, ABC):
    pass