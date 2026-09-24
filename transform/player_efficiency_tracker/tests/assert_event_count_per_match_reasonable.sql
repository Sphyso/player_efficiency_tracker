{{ config(severity='warn') }}

select
    match_id,
    count(*) as event_count
from {{ ref('fact_match_events') }}
group by match_id
having count(*) not between 5 and 40  -- adjust to your observed range