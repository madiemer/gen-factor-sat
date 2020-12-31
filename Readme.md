# GenFactorSat
This application transforms the problem of deciding whether a number is composite into the satisfiability problem. The transformation is handled in such a way that two factors can be retrieved from the resulting satisfying assignment.

## Usage
The tool was created using Python 3.7.3. Currently, it supports factoring a specified number or generating a pseudorandom number itself. For detailed information on the usage, please refer to:
```
gen_factor_sat --help
```

## Generating CNFs
For the structured generation of multiple CNFs, the scripts create.sh and create_random.sh may be used. The former is mainly useful to generate an instance for specific numbers. For an easier configuration, the numbers are read from a configuration file. This file has to define an array of subdirectories in which the results should be written. For each directory, the numbers have to be defined manually. For the exact format please refer to the example configuration. The last command-line argument may be used to indicate that random numbers should be generated.

Usage:
```
scripts/create.sh <config-file> <out-directory> <random>
```

Example:
```
scripts/create.sh scripts/config.ini out/ false
```

The other script create_random.sh can be used to generate the CNFs of random numbers. Therefore, a given interval is split into several subintervals. Each subinterval corresponds to a unique directory. For each subinterval, the specified number of prime, composite or random numbers are created. The last parameter can be used to indicate that a probabilistic prime test with the specified error probability may be used.

Usage:
```
scripts/create_random.sh <out-directory> <start:stop:step> <random:prime:composite> <error>
```

Example:
```
scripts/create_random.sh out/ 10000:1000000:10 0:3:7 0.0
```