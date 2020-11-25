import csv
import functools
import os
import timeit

from gen_factor_sat.factoring_sat import factorize_number

METRICS = 'metrics.csv'
METRICS_SCHEMA = ['Version', 'Number', 'Number length', 'Variables', 'Clauses', 'Runs', 'Avg. Time[ms]']

TIMINGS = 'timings.csv'
TIMINGS_SCHEMA = ['Version', 'Number', 'Run', 'Time [ms]']

VERSION = 'v1-OptZero'
SCENARIOS = [(355888708943419772067, 30), (3315548805509, 100)]  # (Number, Runs)


def append_csv(filename, rows, fieldnames):
    exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not exists:
            writer.writeheader()

        writer.writerows(rows)


for number, runs in SCENARIOS:
    instance = factorize_number(number=number)
    avg_time = timeit.timeit(functools.partial(factorize_number, number=number),
                             number=runs) / runs * 10 ** 3
    csv_data = {
        'Version': VERSION,
        'Number': number,
        'Number length': len(bin(instance.number)[2:]),
        'Variables': instance.number_of_variables,
        'Clauses': len(instance.clauses),
        'Runs': runs,
        'Avg. Time[ms]': '{:.6f}'.format(avg_time)
    }

    append_csv(METRICS, [csv_data], METRICS_SCHEMA)

    # timings = []
    # for i in range(RUNS):
    #     time = timeit.timeit(functools.partial(factoring_sat.factorize_number, number=NUMBER), number=5) / 5
    #     timings.append({
    #         'Version': VERSION,
    #         'Number': NUMBER,
    #         'Run': i + 1,
    #         'Time [ms]': time * 10 ** 3
    #     })
    #
    # append_csv(TIMINGS, timings, TIMINGS_SCHEMA)
