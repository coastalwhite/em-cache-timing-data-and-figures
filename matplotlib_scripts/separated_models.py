#! /usr/bin/env python

from common import (
    PROBE_NAMES,
    average_traces,
    fetch_model_data,
    extract_model,
    NUM_PROBES,
)

import matplotlib.pyplot as plt

DATA_SET = "separated-2probes-rsca-1000"

cache_hit_model = fetch_model_data(DATA_SET, "cache_hit")
cache_miss_model = fetch_model_data(DATA_SET, "cache_miss")

CACHE_HIT_LEN = 7
CACHE_MISS_LEN = 17

MULTIPLICATION_FACTOR = 1000

cache_hit_model = [average_traces(cache_hit_model[i]) for i in range(NUM_PROBES)]
cache_miss_model = [average_traces(cache_miss_model[i]) for i in range(NUM_PROBES)]

cache_hit_model = [
    extract_model(cache_hit_model[i], CACHE_HIT_LEN) for i in range(NUM_PROBES)
]
cache_miss_model = [
    extract_model(cache_miss_model[i], CACHE_MISS_LEN) for i in range(NUM_PROBES)
]

plt.figure(0)
plt.title(
    "Measured Electromagnetic Emissions for Cache Hit Model\n with Seperated Cache and Core"
)
for i, probe_name in enumerate(PROBE_NAMES):
    plt.plot(cache_hit_model[i] * MULTIPLICATION_FACTOR, label=probe_name)
plt.xlabel("Samples / Time Unit")
plt.ylabel("Electromagnetic Emissions (mV)")
plt.legend()
plt.tight_layout()

plt.savefig("./figures/cache_hit.pdf")

plt.figure(1)
plt.title(
    "Measured Electromagnetic Emissions for Cache Miss Model\n with Seperated Cache and Core"
)
for i, probe_name in enumerate(PROBE_NAMES):
    plt.plot(cache_miss_model[i] * MULTIPLICATION_FACTOR, label=probe_name)
plt.ylabel("Electromagnetic Emissions (mV)")
plt.legend()
plt.tight_layout()

plt.savefig("./figures/cache_miss.pdf")

# plt.show()