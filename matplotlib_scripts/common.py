from typing import List
import numpy as np
import numpy.typing as npt

BASE_PATH = "./extracted"
PROBE_NAMES = [
    'Cache',
    'Core',
]
NUM_PROBES = len(PROBE_NAMES)

def fetch_model_data(dataset: str, model: str) -> npt.NDArray[np.float64]:
    file_name = f"{BASE_PATH}/{dataset}/models/raw_data/{model}-triggered.npy"
    return np.load(file_name)

def fetch_hw_data(dataset: str) -> npt.NDArray[np.float64]:
    file_name = f"{BASE_PATH}/{dataset}/data.npy"
    return np.load(file_name)

def extract_model(model: npt.NDArray[np.float64], length: int) -> npt.NDArray[np.float64]:
    WINDOW_START = 109
    return model[WINDOW_START:WINDOW_START + length]

def average_traces(traces):
    return np.mean(traces, axis=0)

def sliding_window(
    trace: npt.NDArray[np.float64],
    model: npt.NDArray[np.float64],
    do_y_shift = False,
):
    """
    Calculate the square difference of between the `model` subtrace and each
    point of the `trace`. The `do_y_shift` parameter allows to compensate for a
    constant y offset in the trace / subtrace and will automatically find the
    minimum value for each subtrace matching.
    """
    window_size = len(model)
    num_values = len(trace) - window_size
    values = np.zeros(num_values)

    if do_y_shift:
        for i in range(num_values):
            subtrace = trace[i:i+window_size]
            dtrace = subtrace - model

            # V = sum j<window_size : (|a_j - b_j| + x)^2
            # Xmin = - (sum |a_j - b_j|) / (sum |a_j - b_j|^2)
            quot = np.sum(dtrace)
            div = window_size

            # Derived with the Quadratic Formula
            x_min = quot / div
            
            v = np.sum(np.square(dtrace - np.repeat(x_min, window_size)))
            
            # Normalize
            values[i] = np.sqrt(v / window_size)
    else:
        for i in range(num_values):
            # V = sum j<window_size : (a_j - b_j)^2
            v = np.sum(np.square(trace[i:i+window_size] - model))

            # Normalize
            values[i] = np.sqrt(v / window_size)

    return values

def sliding_windows_to_measure(
    sw0: npt.NDArray[np.float64],
    sw1: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    assert len(sw0) == len(sw1)
    sw_len = len(sw0)
    
    result = np.empty(sw_len)

    # Calculate measure
    for i in range(sw_len):
        v0 = sw0[i]
        v1 = sw1[i]

        assert v0 != 0.0
        assert v1 != 0.0

        result[i] = np.sqrt((1 / (v0**2)) + (1 / (v1**2)))

    return result

def normalize_over_several(traces: List[npt.NDArray[np.float64]]) -> List[npt.NDArray[np.float64]]:
    maximum = np.max([np.max(trace) for trace in traces])

    return [
        trace / maximum
        for trace in traces
    ]
