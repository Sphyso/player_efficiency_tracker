with ranked_players as (

    select
        player_id,
        player_name,
        row_number() over (
            partition by player_id
            order by match_id desc
        ) as rn
    from {{ ref('stg_player_match_stats') }}

)

select
    player_id,
    player_name
from ranked_players
where rn = 1