import csv
import os
import timeit
import functools

from gen_factor_sat import factoring_sat

METRICS = 'metrics.csv'
METRICS_SCHEMA = ['Version', 'Number', 'Number length', 'Variables', 'Clauses', 'Runs', 'Avg. Time[ms]']

TIMINGS = 'timings.csv'
TIMINGS_SCHEMA = ['Version', 'Number', 'Run', 'Time [ms]']

VERSION = 'v1'
NUMBER = 355888708943419772067  # Randomly chosen
RUNS = 30


def append_csv(filename, rows, fieldnames):
    exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not exists:
            writer.writeheader()

        writer.writerows(rows)


instance = factoring_sat.factorize_number(number=NUMBER)
avg_time = timeit.timeit(functools.partial(factoring_sat.factorize_number, number=NUMBER), number=RUNS) / RUNS * 10 ** 3
csv_data = {
    'Version': VERSION,
    'Number': NUMBER,
    'Number length': len(bin(instance.number)[2:]),
    'Variables': len(instance.variables),
    'Clauses': len(instance.clauses),
    'Runs': RUNS,
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
