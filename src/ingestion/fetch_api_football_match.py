import requests
import os
import json

KEY_FILE_PATH = "api_key.txt"
FIXTURE_ID = 1145510
OUTPUT_DIR = "sandbox"

# Read the API key from the file and strip any accidental whitespace/newlines
if os.path.exists(KEY_FILE_PATH):
    with open(KEY_FILE_PATH, "r") as file:
        api_key = file.read().strip()
else:
    raise FileNotFoundError(f"Could not find '{KEY_FILE_PATH}' in the root directory.")

url = "https://v3.football.api-sports.io/fixtures"

headers = {
    'x-apisports-key': api_key
}

params = {
    'id': FIXTURE_ID
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()

    if data.get('errors'):
        print("API errors:", data['errors'])

    matches = data.get('response', [])

    if not matches:
        print(f"No match found for fixture ID {FIXTURE_ID}.")
    else:
        # Make sure the sandbox folder exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        output_path = os.path.join(OUTPUT_DIR, f"match_{FIXTURE_ID}.json")

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