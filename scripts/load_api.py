"""Send a steady stream of readings to the API so Prometheus has traffic to record.

Distributions are copied from data_simulator/producer.py so the model receives
input that matches what it was trained on.
"""

import random
import time

import numpy as np
import requests

URL = "http://localhost:8000/score"
SENSORS = ["sensor_01", "sensor_02", "sensor_03", "sensor_04"]
ANOMALY_PROBABILITY = 0.03

# Same per-sensor baseline ranges the Kafka producer uses
baselines = {
    s: (round(random.uniform(60, 75), 1), round(random.uniform(0.8, 1.2), 2))
    for s in SENSORS
}

print("Sending readings to the API. Press Ctrl+C to stop.")

while True:
    for sensor_id in SENSORS:
        base_temp, base_vib = baselines[sensor_id]
        temperature = base_temp + np.random.normal(0, 0.5)
        vibration = base_vib + np.random.normal(0, 0.05)

        if random.random() < ANOMALY_PROBABILITY:
            if random.random() < 0.5:
                temperature += random.uniform(8, 15)
            else:
                vibration += random.uniform(1.5, 3.0)

        try:
            requests.post(
                URL,
                json={
                    "sensor_id": sensor_id,
                    "temperature": round(float(temperature), 3),
                    "vibration": round(float(vibration), 3),
                },
                timeout=5,
            )
        except requests.RequestException as exc:
            print("Request failed:", exc)

    time.sleep(1)
