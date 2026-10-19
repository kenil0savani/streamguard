select
    id,
    sensor_id,
    event_time,
    anomaly_score,
    is_anomaly
from {{ source('public', 'scored_events') }}
