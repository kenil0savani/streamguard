with events as (

    select * from {{ ref('fct_anomaly_events') }}

),

aggregated as (

    select
        sensor_id,
        event_hour,
        count(*)                                                      as total_events,
        sum(case when is_anomaly then 1 else 0 end)                   as flagged_anomalies,
        sum(case when is_synthetic_anomaly then 1 else 0 end)         as injected_anomalies,
        sum(case when detection_outcome = 'true_positive' then 1 else 0 end)  as true_positives,
        sum(case when detection_outcome = 'false_positive' then 1 else 0 end) as false_positives,
        sum(case when detection_outcome = 'false_negative' then 1 else 0 end) as false_negatives,
        avg(anomaly_score)                                            as avg_anomaly_score
    from events
    group by sensor_id, event_hour

),

final as (

    select
        sensor_id,
        event_hour,
        total_events,
        flagged_anomalies,
        injected_anomalies,
        true_positives,
        false_positives,
        false_negatives,
        avg_anomaly_score,
        round(100.0 * flagged_anomalies  / nullif(total_events, 0), 2) as flagged_rate_pct,
        round(100.0 * injected_anomalies / nullif(total_events, 0), 2) as injected_rate_pct,
        round(100.0 * true_positives / nullif(true_positives + false_negatives, 0), 2) as recall_pct,
        round(100.0 * true_positives / nullif(true_positives + false_positives, 0), 2) as precision_pct
    from aggregated

)

select * from final