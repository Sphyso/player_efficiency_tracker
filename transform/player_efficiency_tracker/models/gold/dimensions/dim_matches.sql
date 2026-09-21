select
    match_id,
    match_date,
    venue_name as venue,
    tournament_stage as stage,
    home_team_id,
    away_team_id,
    home_score,
    away_score
from {{ ref('stg_matches') }}