{{ config(materialized='view') }}

select
    match_id,
    (raw_payload -> 'fixture' ->> 'date')::timestamptz as match_date,
    raw_payload -> 'fixture' -> 'venue' ->> 'name'       as venue_name,
    raw_payload -> 'league' ->> 'round'                  as tournament_stage,
    (raw_payload -> 'teams' -> 'home' ->> 'id')::int      as home_team_id,
    raw_payload -> 'teams' -> 'home' ->> 'name'           as home_team_name,
    (raw_payload -> 'teams' -> 'away' ->> 'id')::int      as away_team_id,
    raw_payload -> 'teams' -> 'away' ->> 'name'           as away_team_name,
    ingested_at
from {{ source('bronze', 'raw_matches') }}