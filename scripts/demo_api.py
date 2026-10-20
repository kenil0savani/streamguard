"""Warm the API's rolling window with normal readings, then compare a normal and an anomalous one."""

import random
import requests

URL = "http://localhost:8000/score"
SENSOR = "sensor_01"

# 40 normal readings fill the 30-event rolling window
for _ in range(40):
    requests.post(
        URL,
        json={
            "sensor_id": SENSOR,
            "temperature": random.gauss(68.0, 0.5),
            "vibration": random.gauss(1.0, 0.05),
        },
    )

normal = requests.post(
    URL, json={"sensor_id": SENSOR, "temperature": 68.2, "vibration": 1.02}
).json()

spike = requests.post(
    URL, json={"sensor_id": SENSOR, "temperature": 95.4, "vibration": 3.2}
).json()

print("normal reading :", normal)
print("temperature spike:", spike)
