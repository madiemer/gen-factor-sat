from pysat.solvers import Solver

from gen_factor_sat import utils


def assign(variables, values):
    for variable, value in zip(variables, values):
        yield variable if value in ('1', True) else -variable


def run_cnf(input_assignment, output_variables, clauses):
    with Solver(name="cadical", bootstrap_with=clauses) as solver:
        if solver.solve(assumptions=input_assignment):
            return list(assignment_to_bin(output_variables, solver.get_model()))
        else:
            return None


def assignment_to_int(variables, assignment):
    return utils.to_int(list(assignment_to_bin(variables, assignment)))


def assignment_to_bin(variables, assignments):
    for variable in variables:
        if isinstance(variable, str):
            yield utils.to_bin_string(variable == '1')
        elif isinstance(variable, int):
            assignment = assignments[abs(variable) - 1]
            assignment = assignment if variable >= 0 else -assignment
            yield utils.to_bin_string(assignment >= 0)
        else:
            raise ValueError("Invalid output: " + variable)
