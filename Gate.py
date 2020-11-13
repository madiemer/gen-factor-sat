import functools

class Gate:
    pass


class AndGate(Gate):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class OrGate(Gate):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class NotGate(Gate):
    def __init__(self, input):
        self.input = input


class ValueGate(Gate):
    def __init__(self, value):
        self.value = value


@functools.lru_cache(maxsize=None)
def fold_tree(gate, f_and, f_or, f_not, f_value):
    if isinstance(gate, AndGate):
        left_result = fold_tree(gate.left, f_and, f_or, f_not, f_value)
        right_result = fold_tree(gate.right, f_and, f_or, f_not, f_value)

        return f_and(left_result, right_result)

    elif isinstance(gate, OrGate):
        left_result = fold_tree(gate.left, f_and, f_or, f_not, f_value)
        right_result = fold_tree(gate.right, f_and, f_or, f_not, f_value)

        return f_or(left_result, right_result)

    elif isinstance(gate, NotGate):
        result = fold_tree(gate.input, f_and, f_or, f_not, f_value)

        return f_not(result)

    else:
        return f_value(gate)
    # elif isinstance(gate, ValueGate):
    #     return f_value(gate.value)
    #
    # else:
    #     raise ValueError("Gate " + gate + " must be of type And, Or, Not or Value")
