
from abc import ABC
from typing import TypeVar, Generic, List

T = TypeVar('T')
S = TypeVar('S')


class AbstractDataType(Generic[T, S], ABC):
    def prepare(self, source_data: S) -> List[T]:
        pass



class DataSource(Generic[T]):
    pass