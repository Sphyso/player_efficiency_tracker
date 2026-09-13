import requests
import json
import os
from pathlib import Path
from src.config import API_KEY

FIXTURE_ID = 1145509
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "sandbox"

url = "https://v3.football.api-sports.io/fixtures"
headers = {'x-apisports-key': API_KEY}
params = {'id': FIXTURE_ID}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()

    if data.get('errors'):
        print("API errors:", data['errors'])

    matches = data.get('response', [])

    if not matches:
        print(f"No match found for fixture ID {FIXTURE_ID}.")
    else:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = OUTPUT_DIR / f"match_{FIXTURE_ID}.json"

        with open(output_path, "w") as out_file:
            json.dump(data, out_file, indent=4)

        match = matches[0]
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        date = match['fixture']['date']

        print(f"Saved match {FIXTURE_ID}: {home} vs {away} ({date})")
        print(f"Written to {output_path}")
else:
    print(f"Error: {response.status_code} - {response.text}")