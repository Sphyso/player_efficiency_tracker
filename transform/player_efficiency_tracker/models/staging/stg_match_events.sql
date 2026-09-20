{{ config(materialized='view') }}

with events as (
    select match_id, jsonb_array_elements(raw_payload -> 'events') as event
    from {{ source('bronze', 'raw_matches') }}
)
select
    match_id,
    event ->> 'type'                          as event_type_raw,
    (event -> 'team' ->> 'id')::int            as team_id,
    (event -> 'time' ->> 'elapsed')::int       as time_elapsed,
    (event -> 'time' ->> 'extra')::int         as time_extra,
    (event -> 'player' ->> 'id')::int          as primary_player_id,
    (event -> 'assist' ->> 'id')::int          as secondary_player_id
from events
where event ->> 'type' in ('Card', 'Goal', 'subst', 'Var')  -- keeping this list in sync with EventType manually for now