import argparse
import sys

import FactorSat

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--seed', nargs='?', type=int)
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

args = parser.parse_args()

result = FactorSat.generate(args.seed)
args.outfile.write(result.to_dimacs())
