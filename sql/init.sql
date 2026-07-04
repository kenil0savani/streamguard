CREATE TABLE IF NOT EXISTS raw_events (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    vibration DOUBLE PRECISION NOT NULL,
    is_synthetic_anomaly BOOLEAN NOT NULL,
    inserted_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scored_events (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    anomaly_score DOUBLE PRECISION NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    inserted_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_raw_events_sensor_time ON raw_events (sensor_id, event_time);
CREATE INDEX IF NOT EXISTS idx_scored_events_sensor_time ON scored_events (sensor_id, event_time);

CREATE SCHEMA IF NOT EXISTS analytics;
