# Silver & Gold Layer Field Definitions — Player Efficiency Tracker

- **On a `subst` event, `player` is the player going OFF and `assist` is the player coming ON.** Not intuitive from the field name — `assist` is being reused as a generic "second person" slot depending on event type. On a `Goal` event, `assist` genuinely means assist. On a `subst` event, it means "player entering."
- **`fouls.committed` can be `null`**, not `0`, even for a player who played 90 minutes (your sample goalkeeper has `null` there). Same pattern likely applies to `goals.total`, `shots`, etc. for positions where that stat doesn't naturally apply. Your Silver transform needs to coalesce nulls to `0` for anything you're summing or averaging — don't let a null silently break `ga_per_90`.
- **`games.substitute`** (boolean, inside `players[].statistics[].games`) is your `is_starter` flag directly — no need to cross-reference the `lineups` block for this, though `lineups.startXI` / `lineups.substitutes` is still useful for formation/position data pre-kickoff.
- **`league.round`** gives you `"Group A - 1"` — this is both tournament stage and group in one string. Split it (e.g. on `" - "`) if you want stage and matchday as separate columns, or store it as-is if you don't need to query them separately.
- Player names appear in two forms: short form in `events`/`lineups` (`"P. Gulácsi"`) and full form in `players[].player.name` (`"Péter Gulácsi"`). Use the `players` block as your source of truth for `dim_players.player_name` since IDs match across all three blocks (`events`, `lineups`, `players`) — join on `player.id`, not name.

---

## Silver Layer

### `silver_events` — only needed for sub-timing extraction

For API-Football, you don't need this for goals/assists/cards/minutes — `players[].statistics` already gives you those aggregated. You only need to walk `events` for one thing: **substitution minute**.

| Field | Type | Source (`response[].events[]`) |
|---|---|---|
| `match_id` | int | `response[].fixture.id` |
| `team_id` | int | `event.team.id` |
| `player_out_id` | int | `event.player.id` (where `type == "subst"`) |
| `player_in_id` | int | `event.assist.id` (where `type == "subst"` — yes, the "assist" field) |
| `minute` | int | `event.time.elapsed` |
| `extra_minute` | int, nullable | `event.time.extra` (stoppage time, e.g. `90+3` → `extra=3`) |

### `silver_player_match` — one row per player per match

This is what `players[].statistics[]` maps to almost directly — minimal transformation needed.

| Field | Type | Source | Notes |
|---|---|---|---|
| `match_id` | int | `fixture.id` | |
| `player_id` | int | `players[].players[].player.id` | |
| `team_id` | int | `players[].team.id` | |
| `is_starter` | bool | `!statistics[0].games.substitute` | |
| `minutes_played` | int | `statistics[0].games.minutes` | direct field |
| `position` | string | `statistics[0].games.position` | |
| `sub_entry_minute` | int, nullable | from `silver_events`: `player_in_id` match → `minute` | null if starter |
| `sub_exit_minute` | int, nullable | from `silver_events`: `player_out_id` match → `minute` | null if finished the match |
| `goals` | int | `statistics[0].goals.total`, **coalesce null → 0** | |
| `assists` | int | `statistics[0].goals.assists`, coalesce null → 0 | |
| `yellow_cards` | int | `statistics[0].cards.yellow` | |
| `red_cards` | int | `statistics[0].cards.red` | |
| `fouls_committed` | int | `statistics[0].fouls.committed`, **coalesce null → 0** | confirmed nullable in your sample |

---

## Gold Layer

### `fact_player_match_performance`

| Field | Type | Notes |
|---|---|---|
| `player_id` | FK → `dim_players` | |
| `match_id` | FK → `dim_matches` | |
| `team_id` | FK → `dim_teams` | |
| `is_starter` | bool | |
| `minutes_played` | int | keep the row even under 15 min — just exclude from `ga_per_90` |
| `sub_entry_minute` | int, nullable | |
| `sub_exit_minute` | int, nullable | |
| `goals` | int | |
| `assists` | int | |
| `yellow_cards` | int | |
| `red_cards` | int | |
| `fouls_committed` | int | |
| `ga_per_90` | numeric | `(goals + assists) / minutes_played * 90`, null if `minutes_played < 15` |
| `fouls_per_card` | numeric | `fouls_committed / yellow_cards`, null if `yellow_cards == 0` |

### `dim_players`

| Field | Source |
|---|---|
| `player_id` | `players[].players[].player.id` |
| `player_name` | `players[].players[].player.name` (full form — this block, not `events`/`lineups`) |
| `position` | `statistics[0].games.position` |
| `national_team_id` | `players[].team.id` |

### `dim_teams`

| Field | Source |
|---|---|
| `team_id` | `teams.home.id` / `teams.away.id` |
| `country_name` | `teams.home.name` / `teams.away.name` |
| `tournament_group` | `league.round`, e.g. split `"Group A - 1"` → `"Group A"` |

### `dim_matches`

| Field | Source |
|---|---|
| `match_id` | `fixture.id` |
| `match_date` | `fixture.date` |
| `tournament_stage` | `league.round` (or the split-out stage portion, if you split group/stage) |
| `venue` | `fixture.venue.name` (also has `.id` and `.city` if you want those) |
| ~~`referee`~~ | dropped — present in `fixture.referee` but out of scope |

---

## One thing to check on your end

Your sample only had 18 events total for a full match — that's on the low side (no fouls or offsides logged as discrete events, only cards/goals/subs/VAR). Confirm whether that's normal for API-Football's free tier on this competition, or whether you're missing an `events` filter somewhere. It doesn't block anything since `fouls_committed` comes from the aggregated `statistics` block, not from `events` — but it's worth double-checking you're not silently missing data you'll want later. Also worth confirming: your sample has a `"Var"` / `"Goal confirmed"` event right after a `"Goal"` event — make sure your parser doesn't count that as a second goal.
