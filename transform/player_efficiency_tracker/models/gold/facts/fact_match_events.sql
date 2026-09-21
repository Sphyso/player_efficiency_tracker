select
    {{ dbt_utils.generate_surrogate_key(['match_id', 'event_seq']) }} as event_id,
    match_id,
    team_id,
    primary_player_id,
    secondary_player_id as related_player_id,
    case
        when event_type_raw = 'Goal' and event_detail_raw ilike '%own%'     then 'own_goal'
        when event_type_raw = 'Goal' and event_detail_raw ilike '%penalty%' then 'penalty_goal'
        when event_type_raw = 'Goal'                                        then 'goal'
        when event_type_raw = 'Card' and event_detail_raw ilike '%red%'    then 'red_card'
        when event_type_raw = 'Card' and event_detail_raw ilike '%yellow%' then 'yellow_card'
        when event_type_raw = 'subst'                                       then 'substitution'
        when event_type_raw = 'Var'                                         then 'var_review'
        else 'other'
    end as event_type,
    event_type_raw,
    event_detail_raw,
    time_elapsed as elapsed_minute,
    time_extra as added_time_minute
from {{ ref('stg_match_events') }}