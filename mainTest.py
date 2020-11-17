import time

import SATGenerator
import Strategy
from Multiplication import karatsuba, wallace_tree


def run_eval(x, y, func):
    bin_x = bin(y)[2:]
    bin_y = bin(x)[2:]

    strategy = Strategy.EvalStrategy()
    result = func(bin_x, bin_y, strategy)

    bin_result = ''.join(result)
    print(int(bin_result, 2))


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


number = SATGenerator.generate_number(seed=1)
variables, clauses = SATGenerator.factoring_to_sat(number)[0:2]
dimacs = SATGenerator.result_to_dimacs(variables, clauses)

print(dimacs)

x = 10 ** 10
y = 10 ** 10

print(SATGenerator.generate_number(0))

print("Normal evaluation")
run_eval(x, y, wallace_tree)
run_eval(x, y, karatsuba)
print()

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
