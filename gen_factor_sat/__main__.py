import argparse
import sys

from gen_factor_sat import factoring_sat

commands = ['number', 'random']

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

# Commands
subparsers = parser.add_subparsers(dest='command', required=True)

parser_number = subparsers.add_parser(commands[0])
parser_number.add_argument('value', type=int)

parser_random = subparsers.add_parser(commands[1])
parser_random.add_argument('-s', '--seed', nargs='?', type=int)
parser_random.add_argument('max_value', metavar='max-value', type=int)

args = parser.parse_args()

if args.command == commands[0]:
    result = factoring_sat.factorize_number(args.value)
    args.outfile.write(result.to_dimacs())
elif args.command == commands[1]:
    result = factoring_sat.factorize_random_number(args.max_value, args.seed)
    args.outfile.write(result.to_dimacs())
else:
    parser.error('Invalid command: ' + str(args.command))
