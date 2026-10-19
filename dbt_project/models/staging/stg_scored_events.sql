with source as (

    select * from {{ source('streamguard_raw', 'scored_events') }}

),

renamed as (

    select
        id              as scored_event_id,
        sensor_id,
        event_time,
        anomaly_score,
        is_anomaly,
        inserted_at     as scored_at
    from source

)

select * from renamed
