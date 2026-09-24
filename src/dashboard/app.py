import os
import streamlit as st

# Reuses the same env var names your `ingestion` service already sets in
# docker-compose.yml. Defaults match the host-mapped port (5433) so this
# also runs unmodified outside Docker.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "euro24_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

conn = st.connection("euro24_tracker", type="sql", url=DB_URL)


def get_teams():
    df = conn.query(
        "select distinct team_name from gold.dim_teams order by team_name",
        ttl="1h",
    )
    return df["team_name"].tolist()


def get_positions():
    df = conn.query(
        """
        select distinct position
        from gold.fact_player_match_stats
        where position is not null
        order by position
        """,
        ttl="1h",
    )
    return df["position"].tolist()


def _in_clause(prefix, values):
    """
    Build a safe parameterized IN clause: (placeholder_sql, params_dict).
    Only placeholder NAMES (":team_0", ":team_1", ...) are interpolated into
    the SQL string, generated from the list length -- never from the values
    themselves. The actual values always go through parameter binding, so
    this is not a SQL-injection risk despite the f-string.
    """
    placeholders = ", ".join(f":{prefix}_{i}" for i in range(len(values)))
    params = {f"{prefix}_{i}": v for i, v in enumerate(values)}
    return placeholders, params


def get_leaderboard(teams, positions, min_minutes):
    team_sql, team_params = _in_clause("team", teams)
    pos_sql, pos_params = _in_clause("pos", positions)

    query = f"""
        with player_positions as (
            select
                player_id,
                position,
                row_number() over (
                    partition by player_id order by match_id desc
                ) as rn
            from gold.fact_player_match_stats
        ),

        -- A player's position can vary match to match since it lives on the
        -- fact table, not a dim. Pick their most recent one (same pattern
        -- dim_players.sql already uses for player_name) so the tournament
        -- aggregate below has exactly one row per player, not one per
        -- (player, position) combination.
        primary_position as (
            select player_id, position
            from player_positions
            where rn = 1
        ),

        -- Sum raw counts across all matches FIRST, then compute the per-90
        -- rate at the tournament grain. Averaging the already-computed
        -- per-match goals_assists_per_90 values would be wrong: it would
        -- weight a 5-minute substitute cameo the same as a full 90-minute
        -- match.
        agg as (
            select
                player_id,
                team_id,
                sum(minutes_played) as minutes_played,
                sum(goals) as goals,
                sum(assists) as assists,
                sum(yellow_cards) as yellow_cards,
                sum(red_cards) as red_cards,
                sum(fouls_committed) as fouls_committed
            from gold.fact_player_match_stats
            group by player_id, team_id
        )

        select
            p.player_name,
            t.team_name,
            pp.position,
            agg.minutes_played,
            agg.goals,
            agg.assists,
            (agg.goals + agg.assists) * 90.0
                / nullif(agg.minutes_played, 0) as goals_assists_per_90,
            agg.yellow_cards,
            agg.red_cards,
            agg.fouls_committed,
            (agg.yellow_cards * 1 + agg.red_cards * 3 + agg.fouls_committed * 0.25)
                * 90.0 / nullif(agg.minutes_played, 0) as disciplinary_risk_per_90
        from agg
        join gold.dim_players p on agg.player_id = p.player_id
        join gold.dim_teams t on agg.team_id = t.team_id
        join primary_position pp on agg.player_id = pp.player_id
        where t.team_name in ({team_sql})
          and pp.position in ({pos_sql})
          and agg.minutes_played >= :min_minutes
        order by goals_assists_per_90 desc
    """

    params = {**team_params, **pos_params, "min_minutes": min_minutes}
    return conn.query(query, params=params, ttl="10m")


st.set_page_config(page_title="WC Player Efficiency Tracker", layout="wide")
st.title("2024 Euros — Player Efficiency & Disciplinary Tracker")

with st.sidebar:
    st.header("Filters")
    all_teams = get_teams()
    all_positions = get_positions()

    selected_teams = st.multiselect("Team", all_teams, default=all_teams)
    selected_positions = st.multiselect("Position", all_positions, default=all_positions)
    min_minutes = st.slider("Minimum minutes played", 0, 600, 90, step=15)

# Guard against an empty IN () clause if the user clears a filter entirely.
if not selected_teams or not selected_positions:
    st.warning("Select at least one team and one position to see results.")
    st.stop()

leaderboard = get_leaderboard(selected_teams, selected_positions, min_minutes)

tab1, tab2 = st.tabs(["Efficiency Leaderboard", "Disciplinary Risk"])

with tab1:
    st.subheader("Top players by Goals + Assists per 90")
    st.dataframe(
        leaderboard[[
            "player_name", "team_name", "position", "minutes_played",
            "goals", "assists", "goals_assists_per_90",
        ]],
        use_container_width=True,
    )
    st.bar_chart(
        leaderboard.head(15).set_index("player_name")["goals_assists_per_90"]
    )

with tab2:
    st.subheader("Highest disciplinary risk")
    risk_sorted = leaderboard.sort_values("disciplinary_risk_per_90", ascending=False)
    st.dataframe(
        risk_sorted[[
            "player_name", "team_name", "yellow_cards", "red_cards",
            "fouls_committed", "disciplinary_risk_per_90",
        ]],
        use_container_width=True,
    )
    st.bar_chart(
        risk_sorted.head(15).set_index("player_name")["disciplinary_risk_per_90"]
    )

