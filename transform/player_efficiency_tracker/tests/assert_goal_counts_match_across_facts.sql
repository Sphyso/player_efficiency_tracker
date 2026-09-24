with stats_goals as (
    select match_id, sum(goals) as goals_from_stats
    from {{ ref('fact_player_match_stats') }}
    group by match_id
),
event_goals as (
    select match_id, count(*) as goals_from_events
    from {{ ref('fact_match_events') }}
    where event_type = 'goal'
    group by match_id
)
select
    coalesce(s.match_id, e.match_id) as match_id,
    s.goals_from_stats,
    e.goals_from_events
from stats_goals s
full outer join event_goals e using (match_id)
where s.goals_from_stats != e.goals_from_events