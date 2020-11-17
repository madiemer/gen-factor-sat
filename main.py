import operator as op

import Gate
import Strategy
from Multiplication import karatsuba, wallace_tree
import time

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

    # Variable 0 cannot be negated
    sym_x = list(range(1, len(bin_x) + 1))
    sym_y = list(range(len(bin_x) + 1, len(bin_x) + len(bin_y) + 1))

    strategy = Strategy.CircuitStrategy()
    circuit = func(sym_x, sym_y, strategy)

    assignment = {}
    for x, a in zip(sym_x, bin_x):
        assignment[x] = a == '1'

    for y, a in zip(sym_y, bin_y):
        assignment[y] = a == '1'

    bin_result = ''.join(eval_circuit(circuit, assignment))
    print(int(bin_result, 2))


def eval_circuit(circuit, assignment):
    for gate in circuit:
        gateResult = Gate.fold_tree(gate, op.and_, op.or_, op.not_, lambda x: assignment[x])
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
    print("Number of variables: " + str(-strategy.variables[0]))
    print("Clauses: " + str(len(strategy.clauses)))

    # for clause in strategy.clauses:
    #     print(*clause, end=" 0\n")


# Needs trampoline
def run_tseitin_circuit(x, y, func):
    bin_x = bin(y)[2:]
    bin_y = bin(x)[2:]

    # Variable 0 cannot be negated
    sym_x = list(range(1, len(bin_x) + 1))
    sym_y = list(range(len(bin_x) + 1, len(bin_x) + len(bin_y) + 1))

    strategy = Strategy.CircuitStrategy()
    circuit = func(sym_x, sym_y, strategy)

    tseitin, result = tseitin_circuit(circuit, sym_x + sym_y)

    # print("Result in variables: " + str(result))
    print("Number of variables:" + str(-tseitin.variables[0]))
    print("Clauses:")

    # for clause in tseitin.clauses:
    #     print(*clause, end=" 0\n")


def tseitin_circuit(circuit, variables):
    strategy = Strategy.TseitinStrategy(variables)

    result = []
    for gate in circuit:
        gateResult = Gate.fold_tree(gate, strategy.wire_and, strategy.wire_or, strategy.wire_not, lambda x: x)
        result.append(gateResult)

    return strategy, result


x = 10**10
y = 10**10

print("Normal evaluation")
run_eval(x, y, wallace_tree)
run_eval(x, y, karatsuba)
print()

# print("Circuit evaluation")
# run_circuit(x, y, wallace_tree)
# run_circuit(x, y, karatsuba)
# print()

print("Tseitin evaluation")
run_tseitin(x, y, wallace_tree)

timings = []
for i in range(10):
    start = time.time_ns()
    run_tseitin(x, y, karatsuba)
    end = time.time_ns()
    timings.append((end - start) / 1e6)

print(sum(timings) / len(timings))

print()

# print("Tseitin circuit evaluation")
# run_tseitin_circuit(x, y, wallace_tree)
# run_tseitin_circuit(x, y, karatsuba)
# print()