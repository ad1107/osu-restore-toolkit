import os
import re
import csv
import requests
import json
from datetime import timedelta

# Replace these with your actual osu! API credentials and target user ID
CLIENT_ID = "ID"
CLIENT_SECRET = "SECRET"
USER_ID = "USERID"
API_URL = f"https://osu.ppy.sh/api/v2/users/{USER_ID}/beatmapsets/most_played"

# Directories and filenames
download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_JSON = os.path.join(download_dir, "output.json")
ID_TXT = os.path.join(download_dir, "ID.txt")
CSV_FILE = os.path.join(download_dir, "Beatmaps.csv")


def get_access_token(client_id, client_secret):
    """
    Obtain an access token from the osu! API using client credentials.
    """
    token_url = "https://osu.ppy.sh/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public",
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print("Error obtaining token:", response.status_code, response.text)
        return None


def fetch_api_data(url, access_token):
    """
    Send a GET request to the provided API URL with the proper Authorization header.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response


def fetch_all_data():
    """
    Paginate through the API, fetch all data, and export it to 'output.json'.
    """
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    if not token:
        return None

    print("Access token obtained successfully.")

    all_data = []
    limit = 50
    offset = 0

    while True:
        paginated_url = f"{API_URL}?limit={limit}&offset={offset}"
        print(f"Fetching data from: {paginated_url}")
        response = fetch_api_data(paginated_url, token)
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()
        # If no data is returned, we have reached the end.
        if not data:
            break

        all_data.extend(data)
        print(f"Fetched {len(data)} results.")

        if len(data) < limit:
            break

        offset += limit

    with open(OUTPUT_JSON, "w") as outfile:
        json.dump(all_data, outfile, indent=4)
    print(f"\nData exported to {OUTPUT_JSON}")
    return all_data


def get_username(user_id, access_token):
    """
    Fetches user data from the osu! API v2 and returns the username.
    """
    user_url = f"https://osu.ppy.sh/api/v2/users/{user_id}"
    response = fetch_api_data(user_url, access_token)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("username", "Unknown")
    else:
        print("Error fetching user data:", response.status_code, response.text)
        return "Unknown"


def seconds_to_mmss(seconds):
    """
    Convert seconds to mm:ss format.
    """
    try:
        td = timedelta(seconds=int(seconds))
        total_minutes = td.seconds // 60
        secs = td.seconds % 60
        return f"{total_minutes:02d}:{secs:02d}"
    except Exception:
        return "00:00"


def parse_and_export():
    """
    Parse the exported JSON data to produce:
      - ID.txt: unique beatmapset IDs (one per line)
      - Beatmaps.csv: a CSV with desired fields.
    """
    # Load JSON data
    with open(OUTPUT_JSON, "r") as infile:
        data = json.load(infile)

    # Use a set to collect unique beatmapset IDs
    unique_ids = set()
    # Prepare CSV rows list
    csv_rows = []

    # We'll fetch user username first.
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    username = get_username(USER_ID, token) if token else "Unknown"

    # CSV header row (with a title row)
    header_title = f"Beatmaps Played by {username}"
    headers = [
        "Index",
        "Username",
        "User ID",
        "Beatmapset Name",
        "Beatmapset ID",
        "Beatmapset Artist",
        "Beatmap Creator",
        "Beatmap Difficulty Title",
        "Beatmap Difficulty ID",
        "Mode",
        "Status",
        "Length",
        "Star Rating",
        "Retry Count",
        "Download Link"
    ]
    csv_rows.append([header_title])
    csv_rows.append(headers)

    # Loop through each item in the JSON data.
    for idx, item in enumerate(data, start=1):
        # For unique IDs file: we take beatmapset_id from the beatmap object.
        beatmapset_id = item.get("beatmap", {}).get("beatmapset_id", "N/A")
        unique_ids.add(str(beatmapset_id))

        # Extract other fields from the JSON.
        beatmapset_name = item.get("beatmapset", {}).get("title", "N/A")
        beatmapset_artist = item.get("beatmapset", {}).get("artist", "N/A")
        beatmap_creator = item.get("beatmapset", {}).get("creator", "N/A")
        beatmap_difficulty_title = item.get("beatmap", {}).get("version", "N/A")
        beatmap_difficulty_id = item.get("beatmap", {}).get("id", "N/A")
        mode = item.get("beatmap", {}).get("mode", "N/A")
        status = item.get("beatmap", {}).get("status", "N/A")
        total_length_sec = item.get("beatmap", {}).get("total_length", 0)
        length_formatted = seconds_to_mmss(total_length_sec)
        star_rating = item.get("beatmap", {}).get("difficulty_rating", "N/A")
        retry_count = item.get("count", "N/A")
        download_link = f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}#{mode}/{beatmap_difficulty_id}"

        csv_rows.append([
            idx,
            username,
            USER_ID,
            beatmapset_name,
            beatmapset_id,
            beatmapset_artist,
            beatmap_creator,
            beatmap_difficulty_title,
            beatmap_difficulty_id,
            mode,
            status,
            length_formatted,
            star_rating,
            retry_count,
            download_link
        ])

    # Write unique IDs to ID.txt
    with open(ID_TXT, "w") as idfile:
        for uid in sorted(unique_ids):
            idfile.write(uid + "\n")
    print(f"Unique beatmapset IDs exported to {ID_TXT}")

    # Write CSV data to Beatmaps.csv
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in csv_rows:
            writer.writerow(row)
    print(f"CSV exported to {CSV_FILE}")


def main():
    # Step 1: Fetch and export raw API data
    data = fetch_all_data()
    if data is None:
        print("No data fetched. Exiting.")
        return

    # Step 2: Parse and export ID.txt and Beatmaps.csv
    parse_and_export()


if __name__ == "__main__":
    main()
