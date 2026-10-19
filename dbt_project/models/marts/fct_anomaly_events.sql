with scored as (

    select * from {{ ref('stg_scored_events') }}

),

raw as (

    select * from {{ ref('stg_raw_events') }}

),

joined as (

    select
        s.scored_event_id,
        s.sensor_id,
        s.event_time,
        date_trunc('hour', s.event_time) as event_hour,
        r.temperature,
        r.vibration,
        s.anomaly_score,
        s.is_anomaly,
        r.is_synthetic_anomaly,
        case
            when s.is_anomaly and r.is_synthetic_anomaly           then 'true_positive'
            when s.is_anomaly and not r.is_synthetic_anomaly       then 'false_positive'
            when not s.is_anomaly and r.is_synthetic_anomaly       then 'false_negative'
            else 'true_negative'
        end as detection_outcome,
        s.scored_at
    from scored s
    left join raw r
        on s.sensor_id = r.sensor_id
       and s.event_time = r.event_time

)

select * from joined