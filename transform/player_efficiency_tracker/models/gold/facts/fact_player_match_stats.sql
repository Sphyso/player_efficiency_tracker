with subs_in as (

    select
        match_id,
        secondary_player_id as player_id,
        min(time_elapsed) as sub_in_minute
    from {{ ref('stg_match_events') }}
    where event_type_raw = 'subst'
      and secondary_player_id is not null
    group by match_id, secondary_player_id

),

subs_out as (

    select
        match_id,
        primary_player_id as player_id,
        min(time_elapsed) as sub_out_minute
    from {{ ref('stg_match_events') }}
    where event_type_raw = 'subst'
      and primary_player_id is not null
    group by match_id, primary_player_id

),

player_stats as (

    select
        match_id,
        player_id,
        team_id,
        position,
        not is_substitute as started,
        minutes_played,
        goals_total as goals,
        assists,
        yellow_cards,
        red_cards,
        fouls_committed
    from {{ ref('stg_player_match_stats') }}

)

select
    player_stats.match_id,
    player_stats.player_id,
    player_stats.team_id,
    player_stats.position,
    player_stats.started,
    subs_in.sub_in_minute,
    subs_out.sub_out_minute,
    player_stats.minutes_played,
    player_stats.goals,
    player_stats.assists,
    player_stats.yellow_cards,
    player_stats.red_cards,
    player_stats.fouls_committed,
    (player_stats.goals + player_stats.assists) * 90.0
        / nullif(player_stats.minutes_played, 0)                              as goals_assists_per_90,
    (player_stats.yellow_cards * 1
        + player_stats.red_cards * 3
        + player_stats.fouls_committed * 0.25) * 90.0
        / nullif(player_stats.minutes_played, 0)                              as disciplinary_risk_per_90
from player_stats
left join subs_in
    on player_stats.match_id = subs_in.match_id
   and player_stats.player_id = subs_in.player_id
left join subs_out
    on player_stats.match_id = subs_out.match_id
   and player_stats.player_id = subs_out.player_id