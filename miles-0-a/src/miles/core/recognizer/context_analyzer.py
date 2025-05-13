from abc import ABC, abstractmethod

from src.miles.core.context.text_recognize_context import TextRecognizeContext, RecognizeContext
from src.miles.core.recognizer.optimization import RecOptimizationStrategy


class GenericContextAnalyzer(ABC):

    @abstractmethod
    def invoke(self, context: RecognizeContext):
        pass

    def process(self, context: RecognizeContext):
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

    def process(self, context: TextRecognizeContext):
        pass

    def invoke(self, context: TextRecognizeContext):
        pass

class TypedContextAnalyzer(GenericContextAnalyzer):

    @abstractmethod
    def invoke(self, context: TextRecognizeContext):
        pass

    def process(self, context: TextRecognizeContext):
        if context.is_empty():
            context.fail()
        else:
            self.invoke(context)

    def optimization_strategy(self) -> RecOptimizationStrategy:
        return RecOptimizationStrategy.NONE


class WordContextAnalyzer(TypedContextAnalyzer):
    """
    Word Context Analyzer implements matching for a single word
    It checks if the current token equals to the expected one. The token is consumed if it is expected, else the recognition fails
    """
    def __init__(self, word: str):
        self.word = word.lower()

    def invoke(self, context: TextRecognizeContext):
        current_token = context.current()
        if current_token == self.word:
            context.consume()
        else:
            context.fail()

class AnyWordContextAnalyzer(TypedContextAnalyzer):
    """
    Matches one and only one word
    """

    def invoke(self, context: TextRecognizeContext):
        context.consume()

class TextContextAnalyzer(TypedContextAnalyzer):
    """
    Text Context Analyzer implements matching for unbounded text
    """
    def __init__(self):
        pass

    def invoke(self, context: TextRecognizeContext):
        while context.has_any():
            context.consume(interrupted=True)

    def optimization_strategy(self) -> RecOptimizationStrategy:
        return RecOptimizationStrategy.SHORTEST_FIRST


