import pandas as pd
from statsbombpy import sb

# Tells Pandas to show every single row and column
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)        # Prevents columns from wrapping to a new line
pd.set_option('display.max_colwidth', None)

competitions = sb.competitions()
# print(competitions)

matches_2022_wc = sb.matches(competition_id=43, season_id=106)
clean_matches = matches_2022_wc[[
    'match_date', 
    'home_team', 
    'away_team', 
    'home_score', 
    'away_score', 
]].sort_values(by='match_date')

print(matches_2022_wc)