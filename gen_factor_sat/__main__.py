import argparse
import os
import sys

from gen_factor_sat import factoring_sat, number_generator

parser = argparse.ArgumentParser(
    prog='GenFactorSat',
    description='''
    Convert the factorization of a number into a CNF. 
    The resulting CNF is represented in the DIMACS format.
    ''')
parser.add_argument('--version', action='version', version='%(prog)s v{0}'.format(factoring_sat.VERSION))

commands = ['number', 'random']
subparsers = parser.add_subparsers(dest='command', required=True)

parser_number = subparsers.add_parser(commands[0], help="specify a number to be factorized")
parser_number.add_argument('value', type=int, help="the number to be factorized")
parser_number.add_argument('-o', '--outfile', nargs='?', type=str, const='', default='-',
                           help='''
                           redirect the output from stdout to the specified file. If no filename or a directory is
                           specified, a default name is used. (default: stdout)
                           ''')

parser_random = subparsers.add_parser(commands[1], help="generate a random number to be factorized")
parser_random.add_argument('max_value', metavar='max-value', type=int,
                           help='the largest value the random number can take.')
parser_random.add_argument('-m', '--min-value', dest='min_value', type=int, default=2,
                           help='the smallest value the random number can take. (default: 2)')
parser_random.add_argument('-s', '--seed', type=int, help='use the seed to generate a pseudorandom number')
parser_random.add_argument('--prime', dest='prime', action='store_true', default=None,
                           help='''generate a prime number''')
parser_random.add_argument('--no-prime', dest='prime', action='store_false', default=None,
                           help='''generate a composite number''')
parser_random.add_argument('-e', '--error', type=float, default=0.0,
                           help='''
                           the probability that a composite number is declared to be a prime number.
                           If set to 0 a deterministic but slower primality test is used. (default: 0.0)
                           ''')
parser_random.add_argument('-t', '--tries', type=int, default=1000,
                           help='''
                           the number of tries to generate a number with the specified properties. (default: 100)
                           ''')
parser_random.add_argument('-o', '--outfile', nargs='?', type=str, const='', default='-',
                           help='''
                           redirect the output from stdout to the specified file. If no filename or a directory is
                           specified, a default name is used. (default: stdout)
                           ''')

args = parser.parse_args()


def write_cnf(cnf, filename, default_file):
    if filename == '-':
        sys.stdout.write(cnf.to_dimacs())
    else:
        if not filename:
            filename = default_file
        elif not os.path.isfile(filename):
            if not os.path.exists(filename):
                os.makedirs(filename)

            filename = os.path.join(filename, default_file)

        with open(filename, 'w') as file:
            file.write(cnf.to_dimacs())


if args.command == commands[0]:
    result = factoring_sat.factorize_number(args.value)
    default = 'factor_number{0}.cnf'.format(result.number)
    write_cnf(result, args.outfile, default)

elif args.command == commands[1]:
    result = factoring_sat.factorize_random_number(
        max_value=args.max_value,
        min_value=args.min_value,
        seed=args.seed,
        prime=args.prime,
        error=args.error,
        max_tries=args.tries
    )

    number_type = number_generator.fold_number_type(
        result.number,
        v_det_prime='prime',
        v_prob_prime='prob-prime',
        v_det_comp='composite',
        v_prob_comp='composite',
        v_unknown='random'
    )

    default = 'factor_seed{0}_minn{1}_maxn{2}_{3}.cnf'.format(result.seed, result.min_value, result.max_value, number_type)
    write_cnf(result, args.outfile, default)

else:
    parser.error('Invalid command: ' + str(args.command))
