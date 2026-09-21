with teams as (

    select home_team_id as team_id, home_team_name as team_name
    from {{ ref('stg_matches') }}

    union

    select away_team_id as team_id, away_team_name as team_name
    from {{ ref('stg_matches') }}

)

select distinct
    team_id,
    team_name
from teams