with raw as (
    select * from {{ ref('stg_raw_events') }}
),

scored as (
    select * from {{ ref('stg_scored_events') }}
)

select
    raw.sensor_id,
    raw.event_time,
    raw.temperature,
    raw.vibration,
    raw.is_synthetic_anomaly,
    scored.anomaly_score,
    scored.is_anomaly
from raw
inner join scored
    on raw.sensor_id = scored.sensor_id
    and raw.event_time = scored.event_time
