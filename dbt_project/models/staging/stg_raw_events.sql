with source as (

    select * from {{ source('streamguard_raw', 'raw_events') }}

),

renamed as (

    select
        id                   as raw_event_id,
        sensor_id,
        event_time,
        temperature,
        vibration,
        is_synthetic_anomaly,
        inserted_at          as ingested_at
    from source

)

select * from renamed