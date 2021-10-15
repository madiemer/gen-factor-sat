# GenFactorSat
Generate CNF formulas based on the factoring problem to test SAT-Solvers. The application can generate random numbers, but numbers may also be specified. The main part covers the reduction of the factoring problem to SAT. As an intermediate step, the problem is converted into CIRCUIT-SAT. This conversion is achieved by creating a circuit to multiply factor candidates and comparing the resulting product to the given number. Finally, the Tseitin transformation is used to convert the circuit into a CNF.

The resulting formula is satisfiable if and only if there exist two non-trivial factors of the given number. Additionally, based on the way the formula is constructed, the factors can be retrieved from a satisfying assignment. Therefore, the variables representing the input of the circuit, i.e. the factor candidates, are documented.

## Usage
The tool was created using Python 3.7.3 but should run with similar Python versions. Currently, it supports using a given number or generating a pseudorandom number. The resulting CNF is encoded using the DIMACS format and is written to stdout or a specified file. For detailed information on the usage and all configuration options, please refer to:
```
gen_factor_sat --help
```

Alternatively, the application can be imported as a python package. The usage is similar, as the factory methods of the FactoringSat class mimic the command line interface. However, to provide a more convenient usage when working with the results, e.g., calling a SAT-Solver directly from python, the CNF is not converted into DIMACS. Instead, the entire information is stored in the FactoringSat data class.

## Modifications
The CNF generation process can be modified by providing an alternative strategy. Note the additional strategy parameter of the factory methods. The modular design of the evaluation strategies allows exchanging small units without changing the entire implementation. This is achieved by defining dependencies between general modules rather than specific implementations. In the end, when building a specific strategy, an implementation for each required module can be mixed in (almost) independently. For an example, see the instances in the circuit module.

## Generating CNFs
For the structured generation of multiple random CNFs, the create script can be used. Therefore, a given interval is split into several subintervals. Each subinterval corresponds to a unique directory. For each subinterval, the specified number of random, prime, or composite numbers are created. The last parameter defines the error probability that the primality test may have. If set to zero, a deterministic yet slower version is applied.

Usage:
```
scripts/create.sh <out-directory> <start:stop:step> <random:prime:composite> <error>
```

Example:
```
scripts/create.sh out/ 10000:1000000:10 0:3:7 0.0
```

## Evaluation
In order to evaluate the difficulty, we generated 500 random formulas. Starting with numbers out of the interval [10^4, 10^5), we subsequently increased the numbers by the factor 10. For each of the resulting intervals, 50 numbers are drawn at random, of which 35 are composite and 15 are prime. In other words, we used the following command to generate the formulas:
```
scripts/create.sh out/ 10000:100000000000000:10 0:15:35 0.1
```
Note, the create script is not deterministic and will choose new numbers. To reproduce the instances used in our measurement call:
```
gen_factor_sat number <number>
```
The corresponding numbers, as well as the results from the measurements, are located at results/results.csv.