"""
StreamGuard benchmark
---------------------
Measures how many sensor readings the anomaly model can score per second,
and how long one single reading takes.

How to run:
    python benchmark_streamguard.py

It needs only: numpy, scikit-learn
"""

import time

import numpy as np
from sklearn.ensemble import IsolationForest

# ---------------------------------------------------------------
# 1. Make example sensor data (temperature + vibration)
#    50,000 readings, same shape as StreamGuard uses.
# ---------------------------------------------------------------
N_TRAIN = 10_000
N_TEST = 50_000

rng = np.random.default_rng(42)

train_data = np.column_stack([
    rng.normal(loc=45.0, scale=3.0, size=N_TRAIN),   # temperature in C
    rng.normal(loc=0.8, scale=0.2, size=N_TRAIN),    # vibration in mm/s
])

test_data = np.column_stack([
    rng.normal(loc=45.0, scale=3.0, size=N_TEST),
    rng.normal(loc=0.8, scale=0.2, size=N_TEST),
])

print(f"Training the model on {N_TRAIN:,} readings ...")
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(train_data)
print("Training done.\n")

# ---------------------------------------------------------------
# 2. Speed test A: how many readings per second (batch scoring)
# ---------------------------------------------------------------
start = time.perf_counter()
model.decision_function(test_data)
elapsed = time.perf_counter() - start

per_second = N_TEST / elapsed

print("RESULT A - batch scoring")
print(f"  Scored {N_TEST:,} readings in {elapsed:.3f} seconds")
print(f"  Speed: about {per_second:,.0f} readings per second\n")

# ---------------------------------------------------------------
# 3. Speed test B: how long ONE single reading takes
#    (this is the real streaming case, one reading at a time)
# ---------------------------------------------------------------
single_times = []
for i in range(1000):
    one_reading = test_data[i].reshape(1, -1)
    t0 = time.perf_counter()
    model.decision_function(one_reading)
    single_times.append((time.perf_counter() - t0) * 1000)  # in milliseconds

single_times.sort()
average_ms = sum(single_times) / len(single_times)
p95_ms = single_times[int(len(single_times) * 0.95)]

print("RESULT B - single reading scoring")
print(f"  Average time per reading: {average_ms:.2f} milliseconds")
print(f"  95% of readings scored in under: {p95_ms:.2f} milliseconds")
print(f"  That is about {1000 / average_ms:,.0f} readings per second, one by one\n")

print("Write down RESULT A and RESULT B. Those are your CV numbers.")
