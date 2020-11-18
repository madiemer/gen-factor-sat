import argparse
import sys
import time

import FactorSat

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--seed', nargs='?', type=int)
group.add_argument('-n', '--number', nargs='?', type=int)

args = parser.parse_args()

if args.number:
    result = FactorSat.factoring_to_sat(args.number)
else:
    result = FactorSat.generate(args.seed)

args.outfile.write(result.to_dimacs())
