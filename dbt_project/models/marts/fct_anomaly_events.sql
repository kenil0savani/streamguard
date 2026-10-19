with scored as (

    select * from {{ ref('stg_scored_events') }}

),

raw_ranked as (

    select
        raw_event_id,
        sensor_id,
        event_time,
        temperature,
        vibration,
        is_synthetic_anomaly,
        row_number() over (
            partition by sensor_id, event_time
            order by ingested_at desc, raw_event_id desc
        ) as row_num
    from {{ ref('stg_raw_events') }}

),

raw_unique as (

    select * from raw_ranked where row_num = 1

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
    left join raw_unique r
        on s.sensor_id = r.sensor_id
       and s.event_time = r.event_time

)

select * from joined
