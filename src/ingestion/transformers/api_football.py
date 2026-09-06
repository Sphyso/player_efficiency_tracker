from datetime import datetime
import httpx
from src.models.match import Match, TeamInfo, PlayerMatchStats, MatchEvent
from src.models.event_type import EventType
from src.ingestion.id_mapping import resolve_canonical_match_id_api_football

async def ingest_live(fixture_id: int, api_key: str) -> list[Match]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://v3.football.api-sports.io/fixtures",
            params={"id": fixture_id},
            headers={"x-apisports-key": api_key}
        )
        data = resp.json()["response"][0]

    canonical_match_id = resolve_canonical_match_id_api_football(fixture_id)

    match = Match(
        match_id = canonical_match_id,
        match_date = datetime.fromisoformat(data["fixture"]["date"]),
        venue_name = data["fixture"]["venue"]["name"],
        tournament_stage = data["league"]["round"],
        home_team = TeamInfo(
            team_id = data["teams"]["home"]["id"],
            team_name = data["teams"]["home"]["name"]
        ),
        away_team = TeamInfo(
            team_id = data["teams"]["away"]["id"],
            team_name = data["teams"]["away"]["name"]
        ),
        players = _extract_players(data["players"], canonical_match_id),
        events = _extract_events(data["events"], canonical_match_id),
    )
    return [match]


def _extract_players(players_block: list[dict], match_id: int) -> list[PlayerMatchStats]:
    result = []
    for team_entry in players_block:
        team_id = team_entry["team"]["id"]
        for p in team_entry["players"]:
            stats = p["statistics"][0]
            result.append(PlayerMatchStats(
                match_id = match_id,
                player_id = p["player"]["id"],
                player_name = p["player"]["name"],
                team_id = team_id,
                is_substitute = stats["games"]["substitute"],
                minutes_played = stats["games"]["minutes"],
                position = stats["games"]["position"],
                goals_total = stats["goals"]["total"],
                assists = stats["goals"]["assists"],
                yellow_cards = stats["cards"]["yellow"],
                red_cards = stats["cards"]["red"],
                fouls_committed = stats["fouls"]["committed"],
            ))
    return result


def _extract_events(events_block: list[dict], match_id: int) -> list[MatchEvent]:
    result = []
    for e in events_block:
        try:
            result.append(MatchEvent(
                match_id = match_id,
                event_type = EventType(e["type"]),       # flat string: "Card", "Goal", "subst", "Var"
                team_id = e["team"]["id"],
                time_elapsed = e["time"]["elapsed"],
                time_extra = e["time"]["extra"],
                primary_player_id = e["player"]["id"],
                secondary_player_id = e["assist"]["id"],
            ))
        except ValueError:
            continue  # event type not in your EventType enum yet
    return result