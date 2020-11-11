import operator as op

import Gate
import Strategy
from Karatsuba import karatsuba
from WallaceTree import wallace_tree


def run_eval(x, y, func):
    bin_x = bin(y)[2:]
    bin_y = bin(x)[2:]

    strategy = Strategy.EvalStrategy()
    result = func(bin_x, bin_y, strategy)

    bin_result = ''.join(result)
    print(int(bin_result, 2))


def run_circuit(x, y, func):
    bin_x = bin(y)[2:]
    bin_y = bin(x)[2:]

    strategy = Strategy.CircuitStrategy()
    circuit = func(bin_x, bin_y, strategy)

    bin_result = ''.join(eval_circuit(circuit))
    print(int(bin_result, 2))


def eval_circuit(circuit):
    for gate in circuit:
        gateResult = Gate.fold_tree(gate, op.and_, op.or_, op.not_, lambda x: x == '1')
        yield bin(gateResult)[2:]


def run_tseitin(x, y, func):
    bin_x = bin(y)[2:]
    bin_y = bin(x)[2:]

    # Variable 0 cannot be negated
    sym_x = list(range(1, len(bin_x) + 1))
    sym_y = list(range(len(bin_x) + 1, len(bin_x) + len(bin_y) + 1))

    strategy = Strategy.TseitinStrategy(sym_x + sym_y)
    result = func(sym_x, sym_y, strategy)

    print("Result in variables: " + str(result))
    print("Number of variables:" + str(-strategy.variables[0]))
    print("Clauses:")

    for clause in strategy.clauses:
        print(*clause)


# Needs trampoline
# def run_tseitin_circuit(x, y, func):
#     bin_x = bin(y)[2:]
#     bin_y = bin(x)[2:]
#
#     # Variable 0 cannot be negated
#     sym_x = list(range(1, len(bin_x) + 1))
#     sym_y = list(range(len(bin_x) + 1, len(bin_x) + len(bin_y) + 1))
#
#     strategy = Strategy.CircuitStrategy()
#     circuit = func(sym_x, sym_y, strategy)
#
#     tseitin_circuit(circuit, sym_x + sym_y)
#
#
# def tseitin_circuit(circuit, variables):
#     strategy = Strategy.TseitinStrategy(variables)
#
#     result = []
#     for gate in circuit:
#         gateResult = Gate.fold_tree(gate, strategy.wire_and, strategy.wire_or, strategy.wire_not, lambda x: x)
#         result.append(gateResult)
#
#     return strategy, result


x = 1476146
y = 13131414151

print("Normal evaluation")
run_eval(x, y, wallace_tree)
run_eval(x, y, karatsuba)
print()

print("Circuit evaluation")
run_circuit(x, y, wallace_tree)
run_circuit(x, y, karatsuba)
print()

print("Tseitin evaluation")
run_tseitin(x, y, wallace_tree)
run_tseitin(x, y, karatsuba)
print()
