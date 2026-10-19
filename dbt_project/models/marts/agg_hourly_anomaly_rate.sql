select
    sensor_id,
    date_trunc('hour', event_time) as event_hour,
    count(*) as total_events,
    sum(case when is_anomaly then 1 else 0 end) as anomaly_count,
    round(
        sum(case when is_anomaly then 1 else 0 end)::numeric / nullif(count(*), 0),
        4
    ) as anomaly_rate
from {{ ref('fct_anomaly_events') }}
group by 1, 2
order by 1, 2
