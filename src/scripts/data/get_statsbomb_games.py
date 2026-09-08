from statsbombpy import sb

# Fetch all matches for UEFA Euro 2024
euro_matches = sb.matches(competition_id=55, season_id=282)

# Define the requested matchups
requested_games = [
    ("Germany", "Scotland"),
    ("Hungary", "Switzerland"),
    ("Spain", "Croatia"),
    ("Italy", "Albania"),
    ("Poland", "Netherlands"),
    ("Slovenia", "Denmark"),
    ("Serbia", "England"),
    ("Romania", "Ukraine"),
    ("Belgium", "Slovakia"),
    ("Austria", "France")
]

# Filter the dataframe and print the match_ids
for index, row in euro_matches.iterrows():
    home = row['home_team']
    away = row['away_team']

    for team1, team2 in requested_games:
        if (home == team1 and away == team2) or (home == team2 and away == team1):
            print(f"{home} vs {away}: match_id = {row['match_id']}")