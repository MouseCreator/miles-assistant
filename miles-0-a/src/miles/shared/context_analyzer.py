from abc import ABC, abstractmethod
from typing import Any

from src.miles.core.recognizer.optimization import RecOptimizationStrategy
from src.miles.shared.context.text_recognize_context import TextRecognizeContext


class GenericContextAnalyzer(ABC):

    @abstractmethod
    def invoke(self, context: TextRecognizeContext) -> None:
        pass

    @abstractmethod
    def has_result(self) -> bool:
        pass

    def process(self, context: TextRecognizeContext) -> None:
        if context.is_empty():
            context.fail()
        else:
            self.invoke(context)

    def optimization_strategy(self) -> RecOptimizationStrategy:
        return RecOptimizationStrategy.NONE


class AutomaticContextAnalyzer(GenericContextAnalyzer):
    """
    Automatic Context Analyzer implements matching for automatic transitions, e.g. unconditional pointer moving with no token consumption
    """

    def __init__(self):
        pass

    def has_result(self) -> bool:
        return False

    def process(self, context: TextRecognizeContext) -> None:
        pass

    def invoke(self, context: TextRecognizeContext) -> None:
        pass


class TypedContextAnalyzer(GenericContextAnalyzer):

    @abstractmethod
    def invoke(self, context: TextRecognizeContext):
        pass

    def process(self, context: TextRecognizeContext) -> None:
        if context.is_empty():
            context.fail()
        else:
            self.invoke(context)

    def has_result(self) -> bool:
        return True

    def optimization_strategy(self) -> RecOptimizationStrategy:
        return RecOptimizationStrategy.NONE


class WordContextAnalyzer(TypedContextAnalyzer):
    """
    Word Context Analyzer implements matching for a single word
    It checks if the current token equals to the expected one. The token is consumed if it is expected, else the recognition fails
    """

    def __init__(self, word: str):
        self.word = word.lower()

    def invoke(self, context: TextRecognizeContext) -> Any:
        current_token = context.current()
        if current_token.lower() == self.word:
            context.consume()
            context.set_result(current_token)
        else:
            context.fail()


class WordContextAnalyzerFactory(ABC):
    @abstractmethod
    def build(self, word: str) -> TypedContextAnalyzer:
        pass


class DefaultWordContextAnalyzerFactory(WordContextAnalyzerFactory):

    def build(self, word: str) -> TypedContextAnalyzer:
        return WordContextAnalyzer(word)


class AnyWordContextAnalyzer(TypedContextAnalyzer):
    """
    Matches one and only one word
    """

    def invoke(self, context: TextRecognizeContext) -> None:
        current = context.consume()[0]
        context.set_result(current)

class NumberContextAnalyzer(TypedContextAnalyzer):
    """
    Matches one and only numbers
    """

    def invoke(self, context: TextRecognizeContext) -> None:
        current = context.current()
        try:
            a = int(current)
            context.set_result(a)
            context.consume()
        except Exception:
            context.fail()

class TextContextAnalyzer(TypedContextAnalyzer):
    """
    Text Context Analyzer implements matching for unbounded text
    """

    def __init__(self):
        pass

    def invoke(self, context: TextRecognizeContext):
        result = []
        while context.has_any():
            context.consume()
            context.set_result(list(result), interrupted=True)

    def optimization_strategy(self) -> RecOptimizationStrategy:
        return RecOptimizationStrategy.SHORTEST_FIRST
