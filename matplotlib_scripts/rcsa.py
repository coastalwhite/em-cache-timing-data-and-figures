#! /usr/bin/env python

from common import (
    PROBE_NAMES,
    average_traces,
    fetch_model_data,
    extract_model,
    NUM_PROBES,
    fetch_hw_data,
    normalize_over_several,
    sliding_window,
    sliding_windows_to_measure,
)

import numpy as np
import matplotlib.pyplot as plt

DATA_SET = "separated-2probes-rsca-1000"

cache_hit_model = fetch_model_data(DATA_SET, "cache_hit")
cache_miss_model = fetch_model_data(DATA_SET, "cache_miss")

data_set = fetch_hw_data(DATA_SET)

TRACE_CUTOFF_POINT = 575

CACHE_HIT_LEN = 7
CACHE_MISS_LEN = 17

CACHE_HIT_MODEL_COLOR = "blue"
CACHE_MISS_MODEL_COLOR = "orange"

cache_hit_model = [average_traces(cache_hit_model[i]) for i in range(NUM_PROBES)]
cache_miss_model = [average_traces(cache_miss_model[i]) for i in range(NUM_PROBES)]

cache_hit_model = [
    extract_model(cache_hit_model[i], CACHE_HIT_LEN) for i in range(NUM_PROBES)
]
cache_miss_model = [
    extract_model(cache_miss_model[i], CACHE_MISS_LEN) for i in range(NUM_PROBES)
]

data_set = [average_traces(data_set[i]) for i in range(NUM_PROBES)]

# Without Y-Offset Shifting
cache_hit_sliding_window_no_y = [
    sliding_window(data_set[i], cache_hit_model[i], do_y_shift=False)
    for i in range(NUM_PROBES)
]
cache_miss_sliding_window_no_y = [
    sliding_window(data_set[i], cache_miss_model[i], do_y_shift=False)
    for i in range(NUM_PROBES)
]

# With Y-Offset Shifting
cache_hit_sliding_window = [
    sliding_window(data_set[i], cache_hit_model[i], do_y_shift=True)
    for i in range(NUM_PROBES)
]
cache_miss_sliding_window = [
    sliding_window(data_set[i], cache_miss_model[i], do_y_shift=True)
    for i in range(NUM_PROBES)
]


def show_hit_and_miss_zones(tgt = plt, alpha = 0.5):
    pattern = [
        "hit",
        "hit",
        "miss",
        "hit",
        "hit",
        "miss",
        "miss",
        "miss",
        "hit",
        "miss",
    ]

    PATTERN_SPREAD = 28
    PATTERN_OFFSET = 17

    BAR_WIDTH = 28
    HIT_COLOR = "yellowgreen"
    MISS_COLOR = "darkgrey"

    hits = []
    misses = []

    offset = PATTERN_OFFSET
    for i in range(20):
        if i % 2 == 0:
            misses.append(offset)
        else:
            if pattern[int((i - 1) / 2)] == "hit":
                hits.append(offset)
            else:
                misses.append(offset)

        offset += PATTERN_SPREAD

    for i, hit in enumerate(hits):
        start = hit - BAR_WIDTH / 2
        end = hit + BAR_WIDTH / 2

        if i == 0:
            tgt.axvspan(
                start, end, color=HIT_COLOR, alpha=alpha, label="Known Cache Hit"
            )
        else:
            tgt.axvspan(start, end, color=HIT_COLOR, alpha=alpha)

    for i, miss in enumerate(misses):
        start = miss - BAR_WIDTH / 2
        end = miss + BAR_WIDTH / 2

        if i == 0:
            tgt.axvspan(
                start, end, color=MISS_COLOR, alpha=alpha, label="Known Cache Miss"
            )
        else:
            tgt.axvspan(start, end, color=MISS_COLOR, alpha=alpha)


# Figures:
# 1. No Y-Shifting. Cache Hit vs. Cache Miss
# 2. Y-Shifting. Cache Hit vs. Cache Miss
# 3. Individual Probe. Y-Shifting. Core Cache Hit vs. Core Cache Miss
# 4. Individual Probe. Y-Shifting. Cache Cache Hit vs. Cache Cache Miss
# 5. Y-Shifting. 10 Traces, 100 Traces, 1000 Traces.

plt.figure(1)
plt.title(
    """
Confidence in Presence of Cache Hit and Miss Models
over a pattern of cache misses and hits (No Y-Shifting)
""".strip()
)
show_hit_and_miss_zones()

cache_hit_presence_no_y = sliding_windows_to_measure(
    cache_hit_sliding_window_no_y[0], cache_hit_sliding_window_no_y[1]
)
cache_miss_presence_no_y = sliding_windows_to_measure(
    cache_miss_sliding_window_no_y[0], cache_miss_sliding_window_no_y[1]
)

[
    cache_hit_presence_no_y,
    cache_miss_presence_no_y,
] = normalize_over_several(
    [
        cache_hit_presence_no_y,
        cache_miss_presence_no_y,
    ]
)

cache_hit_presence_no_y = cache_hit_presence_no_y[:TRACE_CUTOFF_POINT]
cache_miss_presence_no_y = cache_miss_presence_no_y[:TRACE_CUTOFF_POINT]

plt.plot(cache_hit_presence_no_y, color=CACHE_HIT_MODEL_COLOR, label="Cache Hit")
plt.plot(cache_miss_presence_no_y, color=CACHE_MISS_MODEL_COLOR, label="Cache Miss")
plt.xlabel("Samples / Time Unit")
plt.ylabel("Confidence in Presence of Model")
plt.legend()
plt.tight_layout()

plt.savefig("./figures/presence_rsca_no_y.pdf")

plt.figure(2)
plt.title(
    """
Confidence in Presence of Cache Hit and Miss Models
over a pattern of cache misses and hits (Y-Shifting)
""".strip()
)
show_hit_and_miss_zones()
cache_hit_presence = sliding_windows_to_measure(
    cache_hit_sliding_window[0], cache_hit_sliding_window[1]
)
cache_miss_presence = sliding_windows_to_measure(
    cache_miss_sliding_window[0], cache_miss_sliding_window[1]
)

[
    cache_hit_presence,
    cache_miss_presence,
] = normalize_over_several(
    [
        cache_hit_presence,
        cache_miss_presence,
    ]
)

cache_hit_presence = cache_hit_presence[:TRACE_CUTOFF_POINT]
cache_miss_presence = cache_miss_presence[:TRACE_CUTOFF_POINT]

plt.plot(cache_hit_presence, color=CACHE_HIT_MODEL_COLOR, label="Cache Hit")
plt.plot(cache_miss_presence, color=CACHE_MISS_MODEL_COLOR, label="Cache Miss")
plt.xlabel("Samples / Time Unit")
plt.ylabel("Confidence in Presence of Model")
plt.legend()
plt.tight_layout()

plt.savefig("./figures/presence_rsca.pdf")

for i, probe_name in enumerate(PROBE_NAMES):
    plt.figure(3 + i)
    plt.title(
        f"""
    Confidence in Presence of Cache Hit and Miss Models
    over a pattern of cache misses and hits ({probe_name} Probe)
    """.strip()
    )
    show_hit_and_miss_zones()

    cache_hit_presence_individual = np.reciprocal(cache_hit_sliding_window[i])
    cache_miss_presence_individual = np.reciprocal(cache_miss_sliding_window[i])

    [
        cache_hit_presence_individual,
        cache_miss_presence_individual,
    ] = normalize_over_several(
        [
            cache_hit_presence_individual,
            cache_miss_presence_individual,
        ]
    )

    cache_hit_presence_individual = cache_hit_presence_individual[:TRACE_CUTOFF_POINT]
    cache_miss_presence_individual = cache_miss_presence_individual[:TRACE_CUTOFF_POINT]

    plt.plot(
        cache_hit_presence_individual, color=CACHE_HIT_MODEL_COLOR, label="Cache Hit"
    )
    plt.plot(
        cache_miss_presence_individual, color=CACHE_MISS_MODEL_COLOR, label="Cache Miss"
    )

    plt.xlabel("Samples / Time Unit")
    plt.ylabel("Confidence in Presence of Model")
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"./figures/presence_rsca_{probe_name.lower()}.pdf")


f, axs = plt.subplots(1, 3, sharex=True, sharey=True)
f.suptitle(
    """
Confidence in Presence of Cache Miss Model
for several number of trace amounts
""".strip()
)

amounts = [10, 100, 1000]

data_set = fetch_hw_data(DATA_SET)
amount_data_sets = [
    [average_traces(data_set[i][:amount, :]) for i in range(NUM_PROBES)]
    for amount in amounts
]

amount_sliding_windows = [
    [
        sliding_window(amount_data_sets[j][i], cache_miss_model[i], do_y_shift=True)
        for i in range(NUM_PROBES)
    ]
    for j in range(len(amounts))
]

measures = [
    sliding_windows_to_measure(amount_sliding_windows[i][0], amount_sliding_windows[i][1])
    for i in range(len(amounts))
]

measures = normalize_over_several(measures)

for i, amount in enumerate(amounts):
    p = axs[i]
    p.set_title(label=f"{amount} Traces")
    p.plot(measures[i][:TRACE_CUTOFF_POINT])
    p.set_ylim(0, 1)
    show_hit_and_miss_zones(tgt = p, alpha = 0.25)

f.supxlabel("Samples / Time Unit")
f.supylabel("Confidence in Presence of Model")

plt.tight_layout()

plt.savefig("./figures/presence_rsca_amount_traces.pdf")

# plt.show()