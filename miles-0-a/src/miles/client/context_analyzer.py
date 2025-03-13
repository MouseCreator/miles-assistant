from abc import ABC

from src.miles.core.recognizer.context_analyzer import GenericContextAnalyzer


class ClientContextAnalyzer(GenericContextAnalyzer, ABC):
    pass