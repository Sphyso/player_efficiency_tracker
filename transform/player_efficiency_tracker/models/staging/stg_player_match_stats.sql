{{ config(materialized='view') }}

with team_entries as (
    select match_id, jsonb_array_elements(raw_payload -> 'players') as team_entry
    from {{ source('bronze', 'raw_matches') }}
),
player_entries as (
    select
        match_id,
        (team_entry -> 'team' ->> 'id')::int as team_id,
        jsonb_array_elements(team_entry -> 'players') as player_entry
    from team_entries
)
select
    match_id,
    team_id,
    (player_entry -> 'player' ->> 'id')::int                                        as player_id,
    player_entry -> 'player' ->> 'name'                                             as player_name,
    (player_entry -> 'statistics' -> 0 -> 'games' ->> 'substitute')::boolean         as is_substitute,
    (player_entry -> 'statistics' -> 0 -> 'games' ->> 'minutes')::int                as minutes_played,
    player_entry -> 'statistics' -> 0 -> 'games' ->> 'position'                      as position,
    coalesce((player_entry -> 'statistics' -> 0 -> 'goals' ->> 'total')::int, 0)     as goals_total,
    coalesce((player_entry -> 'statistics' -> 0 -> 'goals' ->> 'assists')::int, 0)   as assists,
    (player_entry -> 'statistics' -> 0 -> 'cards' ->> 'yellow')::int                 as yellow_cards,
    (player_entry -> 'statistics' -> 0 -> 'cards' ->> 'red')::int                    as red_cards,
    coalesce((player_entry -> 'statistics' -> 0 -> 'fouls' ->> 'committed')::int, 0) as fouls_committed
from player_entries