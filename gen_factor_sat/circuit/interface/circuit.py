"""
Basic circuit operations

This module provides interfaces for basic circuit operations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Generic, TypeVar

T = TypeVar('T')
W = TypeVar('W')


class GateStrategy(Generic[T, W], ABC):
    """
    The evaluation strategy for the operations of the standard base.
    """

    @property
    @abstractmethod
    def zero(self) -> T:
        """
        The object representing a zero.

        :return: the zero element
        """
        pass

    @property
    @abstractmethod
    def one(self) -> T:
        """
        The object representing a one.

        :return: the one element
        """
        pass

    @abstractmethod
    def wire_and(self, value_1: T, value_2: T, writer: W) -> T:
        """
        Combine the values using a logical AND.

        :param value_1: the first value to be combined
        :param value_2: the second value to be combined
        :param writer: a writer for stateful operations
        :return: the result of the logical AND
        """
        pass

    @abstractmethod
    def wire_or(self, value_1: T, value_2: T, writer: W) -> T:
        """
        Combine the values using a logical OR.

        :param value_1: the first value to be combined
        :param value_2: the second value to be combined
        :param writer: a writer for stateful operations
        :return: the result of the logical OR
        """
        pass

    @abstractmethod
    def wire_not(self, value: T, writer: W) -> T:
        """
        Negate the value using a logical NOT.

        :param value: the value to be negated
        :param writer: a writer for stateful operations
        :return: the result of the logical NOT
        """
        pass

    def is_constant(self, value: T) -> bool:
        """
        Check whether the value is the zero or one element.

        :param value: the value to be checked
        :return: true if the value is zero or one, otherwise false
        """
        return (value == self.zero) or (value == self.one)

    def is_zero(self, value: T) -> bool:
        """
        Check whether the value is the zero element.

        :param value: the value to be checked
        :return: true if the value is zero, otherwise false
        """
        return value == self.zero

    def is_one(self, value: T) -> bool:
        """
        Check whether the value is the one element.

        :param value: the value to be checked
        :return: true if the value is equal to the one element, otherwise false
        """
        return value == self.one


class SimpleCircuitStrategy(Generic[T, W], ABC):
    """
    The evaluation strategy for simple (1-Bit) operations.
    """

    @abstractmethod
    def half_adder(self, value_1: T, value_2: T, writer: W) -> Tuple[T, T]:
        """
        Calculate the sum of both values.

        :param value_1: the first value to be added
        :param value_2: the second value to be added
        :param writer: a writer for stateful operations
        :return: a tuple consisting of the resulting sum and carry value
        """
        pass

    @abstractmethod
    def full_adder(self, value_1: T, value_2: T, carry: T, writer: W) -> Tuple[T, T]:
        """
        Calculate the sum of both values and the carry.

        :param value_1: the first value to be added
        :param value_2: the second value to be added
        :param carry: the carry value to be added
        :param writer: a writer for stateful operations
        :return: a tuple consisting of resulting the sum and carry value
        """
        pass

    @abstractmethod
    def equality(self, value_1: T, value_2: T, writer: W) -> T:
        """
        Check whether the inputs have the same value.

        :param value_1: the first value to be compared
        :param value_2: the second value to be compared
        :param writer: a writer for stateful operations
        :return: the result of the comparison
        """
        pass

    @abstractmethod
    def xor(self, value_1: T, value_2: T, writer: W) -> T:
        """
        Check whether the inputs have different values.

        :param value_1: the first value to be compared
        :param value_2: the second value to be compared
        :param writer: a writer for stateful operations
        :return: the result of the comparison
        """
        pass


class NBitCircuitStrategy(Generic[T, W], ABC):
    """
    The evaluation strategy for basic operations with N-bit inputs.
    All numbers are unsigned and start with the most significant bit.
    """

    @abstractmethod
    def n_bit_adder(self, number_1: List[T], number_2: List[T], carry: T, writer: W) -> List[T]:
        """
        Calculate the sum of both numbers and the carry.
        The numbers are interpreted as [msb, ..., lsb].

        :param number_1: the first value to be added
        :param number_2: the second value to be added
        :param carry: the carry value to be added
        :param writer: a writer for stateful operations
        :return: the resulting value including an optional carry
        """
        pass

    @abstractmethod
    def subtract(self, number_1: List[T], number_2: List[T], writer: W) -> List[T]:
        """
        Calculate the difference between the first and the second number. Signed
        numbers are not supported. Consequently, the first value must be greater
        than or equal to the second value.
        The numbers are interpreted as [msb, ..., lsb].

        :param number_1: the minued
        :param number_2: the subtrahend
        :param writer: a writer for stateful operations
        :return: the resulting value
        """
        pass

    @abstractmethod
    def n_bit_equality(self, number_1: List[T], number_2: List[T], writer: W) -> T:
        """
        Check whether the inputs have the same number.

        :param number_1: the first value to be compared
        :param number_2: the second value to be compared
        :param writer: a writer for stateful operations
        :return: the result of the comparison
        """
        pass

    @abstractmethod
    def shift(self, number: List[T], shifts: int, writer: W) -> List[T]:
        """
        Shift the number by the specified amount, i.e. add the specified amount
        of zeros at the least significant bit.

        :param number: the number to be shifted
        :param shifts: the number of shifts
        :param writer: a writer for stateful operations
        :return: the shifted number
        """
        pass

    @abstractmethod
    def align(self, number_1: List[T], number_2: List[T], writer: W) -> Tuple[List[T], List[T]]:
        """
        Align both numbers by adding zeros at the most significant bit.

        :param number_1: the first number to be aligned
        :param number_2: the second number to be aligned
        :param writer: a writer for stateful operations
        :return: the aligned numbers
        """
        pass

    @abstractmethod
    def normalize(self, number: List[T]) -> List[T]:
        """
        Remove the leading zeros. Return an empty list if the number is zero.

        :param number: the number to be normalized
        :return: the normalized number
        """
        pass

    def all_zero(self, number: List[T]) -> bool:
        """
        Check whether the number is zero.

        :param number: the number to be checked
        :return: true if the number equals to zero, otherwise false
        """
        return not self.normalize(number)
