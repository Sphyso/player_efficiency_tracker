{{ config(materialized='view') }}

with events as (
    select
        match_id,
        t.ordinality as event_seq,
        t.event       as event
    from {{ source('bronze', 'raw_matches') }},
    jsonb_array_elements(raw_payload -> 'events') with ordinality as t(event, ordinality)
)
select
    match_id,
    event_seq,
    event ->> 'type'                          as event_type_raw,
    event ->> 'detail'                        as event_detail_raw,
    (event -> 'team' ->> 'id')::int            as team_id,
    (event -> 'time' ->> 'elapsed')::int       as time_elapsed,
    (event -> 'time' ->> 'extra')::int         as time_extra,
    (event -> 'player' ->> 'id')::int          as primary_player_id,
    (event -> 'assist' ->> 'id')::int          as secondary_player_id
from events
where event ->> 'type' in ('Card', 'Goal', 'subst', 'Var')