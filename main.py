import argparse
import random
import sys

import SATGenerator

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--seed', nargs='?', type=int)
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

args = parser.parse_args()

if args.seed:
    seed = args.seed
else:
    seed = random.randrange(sys.maxsize)

number = SATGenerator.generate_number(seed=seed)
variables, clauses = SATGenerator.factoring_to_sat(number)[0:2]
dimacs = SATGenerator.result_to_dimacs(variables, clauses)

args.outfile.write(dimacs)
