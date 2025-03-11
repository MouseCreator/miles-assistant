from abc import abstractmethod, ABC

class Recognizer(ABC):
    @abstractmethod
    def recognize(self):
        pass