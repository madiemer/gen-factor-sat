from abc import ABC, abstractmethod
from typing import List, Tuple, Generic, TypeVar

T = TypeVar('T')
W = TypeVar('W')


class GateStrategy(Generic[T, W], ABC):

    @property
    @abstractmethod
    def zero(self) -> T:
        pass

    @property
    @abstractmethod
    def one(self) -> T:
        pass

    @abstractmethod
    def wire_and(self, input_1: T, input_2: T, writer: W) -> T:
        pass

    @abstractmethod
    def wire_or(self, input_1: T, input_2: T, writer: W) -> T:
        pass

    @abstractmethod
    def wire_not(self, input: T, writer: W) -> T:
        pass

    def is_constant(self, value: T) -> bool:
        return (value == self.zero) or (value == self.one)

    def is_zero(self, value: T) -> bool:
        return value == self.zero

    def is_one(self, value: T) -> bool:
        return value == self.one


class SimpleCircuitStrategy(Generic[T, W], ABC):

    @abstractmethod
    def half_adder(self, input_1: T, input_2: T, writer: W) -> Tuple[T, T]:
        pass

    @abstractmethod
    def full_adder(self, input_1: T, input_2: T, carry: T, writer: W) -> Tuple[T, T]:
        pass

    @abstractmethod
    def equality(self, input_1: T, input_2: T, writer: W) -> T:
        pass

    @abstractmethod
    def xor(self, input_1: T, input_2: T, writer: W) -> T:
        pass


class NBitCircuitStrategy(Generic[T, W], ABC):

    @abstractmethod
    def n_bit_adder(self, inputs_1: List[T], inputs_2: List[T], carry: T, writer: W) -> List[T]:
        pass

    @abstractmethod
    def subtract(self, inputs_1: List[T], inputs_2: List[T], writer: W) -> List[T]:
        pass

    @abstractmethod
    def n_bit_equality(self, inputs_1: List[T], inputs_2: List[T], writer: W) -> T:
        pass

    @abstractmethod
    def shift(self, inputs_1: List[T], shifts: int, writer: W) -> List[T]:
        pass

    @abstractmethod
    def align(self, inputs_1: List[T], inputs_2: List[T], writer: W) -> Tuple[List[T], List[T]]:
        pass

    @abstractmethod
    def normalize(self, inputs: List[T]) -> List[T]:
        pass

    def all_zero(self, values: List[T]) -> bool:
        return not self.normalize(values)
