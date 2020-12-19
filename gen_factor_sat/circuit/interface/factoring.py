from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

T = TypeVar('T')
W = TypeVar('W')


class FactoringStrategy(Generic[T, W], ABC):

    @abstractmethod
    def factorize(self, factor_1: List[T], factor_2: List[T], number: List[T], writer: W) -> T:
        pass
