import argparse
import sys

from gen_factor_sat import factoring_sat

parser = argparse.ArgumentParser()

commands = ['number', 'random']
subparsers = parser.add_subparsers(dest='command', required=True)

parser_number = subparsers.add_parser(commands[0])
parser_number.add_argument('value', type=int)
parser_number.add_argument('-o', '--outfile', nargs='?', type=str, const='', default='-')

parser_random = subparsers.add_parser(commands[1])
parser_random.add_argument('-s', '--seed', nargs='?', type=int)
parser_random.add_argument('max_value', metavar='max-value', type=int)
parser_random.add_argument('-o', '--outfile', nargs='?', type=str, const='', default='-')

args = parser.parse_args()


def write_cnf(cnf, filename, default_file):
    if filename == '-':
        sys.stdout.write(cnf.to_dimacs())
    else:
        if not filename:
            filename = default_file

        with open(filename, 'w') as file:
            file.write(cnf.to_dimacs())


if args.command == commands[0]:
    result = factoring_sat.factorize_number(args.value)
    default = 'factor_number{0}.cnf'.format(result.number)
    write_cnf(result, args.outfile, default)

elif args.command == commands[1]:
    result = factoring_sat.factorize_random_number(args.max_value, args.seed)
    default = 'factor_seed{0}_maxn{1}.cnf'.format(result.seed, result.max_value)
    write_cnf(result, args.outfile, default)

else:
    parser.error('Invalid command: ' + str(args.command))
