"""
Simulates a small fleet of IoT sensors (temperature + vibration) publishing
telemetry to a Kafka topic. Occasionally injects synthetic faults (temperature
spikes / vibration surges) so the downstream anomaly model has something real
to catch. The `is_synthetic_anomaly` flag is ground truth for offline
evaluation only — it is never passed to the model.
"""
import json
import os
import random
import time
from datetime import datetime, timezone

import numpy as np
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:19092")
TOPIC = os.getenv("KAFKA_TOPIC", "iot.telemetry")
ANOMALY_PROBABILITY = float(os.getenv("ANOMALY_PROBABILITY", "0.03"))
SENSORS = ["sensor_01", "sensor_02", "sensor_03", "sensor_04"]


def make_producer(retries: int = 15):
    for attempt in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Kafka not ready yet ({exc}); retrying in 3s... [{attempt + 1}/{retries}]")
            time.sleep(3)
    raise RuntimeError(f"Could not connect to Kafka broker at {KAFKA_BROKER}")


def generate_reading(sensor_id: str, baseline_temp: float, baseline_vibration: float) -> dict:
    is_anomaly = random.random() < ANOMALY_PROBABILITY

    temperature = baseline_temp + np.random.normal(0, 0.5)
    vibration = baseline_vibration + np.random.normal(0, 0.05)

    if is_anomaly:
        if random.random() < 0.5:
            temperature += random.uniform(8, 15)   # overheating fault
        else:
            vibration += random.uniform(1.5, 3.0)  # mechanical fault

    return {
        "sensor_id": sensor_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(float(temperature), 3),
        "vibration": round(float(vibration), 3),
        "is_synthetic_anomaly": is_anomaly,
    }


def main() -> None:
    producer = make_producer()
    baselines = {
        s: (round(random.uniform(60, 75), 1), round(random.uniform(0.8, 1.2), 2))
        for s in SENSORS
    }

    print(f"Producing synthetic IoT telemetry to topic '{TOPIC}' on {KAFKA_BROKER}. Ctrl+C to stop.")
    try:
        while True:
            for sensor_id in SENSORS:
                base_temp, base_vib = baselines[sensor_id]
                reading = generate_reading(sensor_id, base_temp, base_vib)
                producer.send(TOPIC, value=reading)
                print(reading)
            producer.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping producer.")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
