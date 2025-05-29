import os
import csv
import requests
import json
from datetime import timedelta
import argparse

# CONFIGURATION
SERVER_ID = 1

# Server List:
# 1: osu! (Bancho v2)
# 2: Akatsuki
# 3: Ripple
# 4: Gatari


USERNAME = "USERNAME_HERE"  # Replace with your osu! username
USER_ID = ""  # Leave blank to use USERNAME, or specify user ID

# If using osu! API, set these credentials
# You can access your client ID and secret from https://osu.ppy.sh/home/account/edit#oauth
CLIENT_ID = "CLIENT_ID_HERE"  # Replace with your actual client ID
CLIENT_SECRET = "CLIENT_SECRET_HERE"  # Replace with your actual client secret

SERVERS = {
    1: {
        "name": "osu! (Bancho v2)",
        "base_url": "https://osu.ppy.sh/api/v2",
        "scores_endpoint": "/users/{user_id}/beatmapsets/most_played",
        "user_endpoint": "/users/{user_id}",
        "auth_required": True,
        "pagination": {"limit_param": "limit", "offset_param": "offset"}
    },
    2: {
        "name": "Akatsuki",
        "base_url": "https://akatsuki.gg/api/v1",
        "scores_endpoint": "/users/scores/best",
        "user_endpoint": "/users/full",
        "auth_required": False,
        "pagination": {"limit_param": "l", "page_param": "p", "name_param": "name", "mode_param": "mode"},
        "modes": [0, 1, 2, 3]
    },
    3: {
        "name": "Ripple",
        "base_url": "https://ripple.moe/api/v1",
        "scores_endpoint": "/users/scores/best",
        "user_endpoint": "/users/full",
        "auth_required": False,
        "pagination": {"limit_param": "l", "page_param": "p", "name_param": "name", "mode_param": "m"},
        "modes": [0, 1, 2, 3]
    },
    4: {
        "name": "Gatari",
        "base_url": "https://osu.gatari.pw/api/v1",
        "scores_endpoint": "/users/scores/best",
        "user_endpoint": "/users/full",
        "auth_required": False,
        "pagination": {"limit_param": "l", "page_param": "p", "name_param": "name", "mode_param": "m"},
        "modes": [0, 1, 2, 3]
    }
}

download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_JSON = os.path.join(download_dir, "output.json")
ID_TXT = os.path.join(download_dir, "ID.txt")
CSV_FILE = os.path.join(download_dir, "Beatmaps.csv")


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and export osu! beatmap data")
    parser.add_argument("--username", type=str, default=USERNAME)
    parser.add_argument("--user-id", type=str, default=USER_ID)
    parser.add_argument("--server", type=int, default=SERVER_ID, choices=list(SERVERS.keys()),
                        help=f"Server: {', '.join([f'{k}-{v['name']}' for k, v in SERVERS.items()])}")
    return parser.parse_args()


def get_access_token():
    response = requests.post("https://osu.ppy.sh/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "public",
    })
    return response.json().get("access_token") if response.status_code == 200 else None


def fetch_api_data(url, access_token=None):
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
    return requests.get(url, headers=headers)


def get_user_id(username, access_token):
    response = fetch_api_data(f"https://osu.ppy.sh/api/v2/users/{username}", access_token)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("id"), user_data.get("username")
    return None, None


def build_api_url(server_config, endpoint, username, limit=50, page=1, user_id=None, mode=None):
    base_url = server_config["base_url"]
    pagination = server_config.get("pagination", {})
    
    # Format endpoint
    if "{user_id}" in endpoint and user_id:
        url = f"{base_url}{endpoint.format(user_id=user_id)}"
    else:
        url = f"{base_url}{endpoint}"
    
    # Build parameters
    params = []
    
    # User parameter
    if "name_param" in pagination and username:
        params.append(f"{pagination['name_param']}={username}")
    
    # Mode parameter (for Akatsuki)
    if mode is not None and "mode_param" in pagination:
        params.append(f"{pagination['mode_param']}={mode}")
    
    # Pagination parameters
    if "limit_param" in pagination:
        params.append(f"{pagination['limit_param']}={limit}")
    
    if "page_param" in pagination:
        params.append(f"{pagination['page_param']}={page}")
    elif "offset_param" in pagination:
        offset = (page - 1) * limit
        params.append(f"{pagination['offset_param']}={offset}")
    
    return f"{url}?{'&'.join(params)}" if params else url


def fetch_server_data(username, user_id, server_id):
    server_config = SERVERS[server_id]
    print(f"Using server: {server_config['name']}")
    
    # Determine which identifier to use (prioritize username)
    target_user = username if username else user_id
    if not target_user:
        print("Error: No username or user ID provided")
        return None
    
    # Handle authentication
    access_token = None
    bancho_user_id = None
    
    if server_config.get("auth_required"):
        access_token = get_access_token()
        if not access_token:
            print("Failed to obtain access token")
            return None
        
        bancho_user_id, actual_username = get_user_id(target_user, access_token)
        if not bancho_user_id:
            print(f"User not found: {target_user}")
            return None
        print(f"Found user: {actual_username} (ID: {bancho_user_id})")
    
    all_data = []
    
    # Handle multi-mode servers
    if server_id in [2, 3, 4] and "modes" in server_config:
        mode_names = ["osu", "taiko", "catch", "mania"]
        for mode in server_config["modes"]:
            print(f"Fetching {mode_names[mode]} scores...")
            
            page = 1
            while page <= 10:  # Reasonable limit
                api_url = build_api_url(server_config, server_config["scores_endpoint"], 
                                      username, 100, page, user_id, mode)
                
                response = fetch_api_data(api_url, access_token)
                if response.status_code != 200:
                    print(f"  Error {response.status_code}: {response.text}")
                    break
                
                data = response.json()
                current_data = data if isinstance(data, list) else data.get("scores", [])
                
                if not current_data:
                    break
                
                all_data.extend(current_data)
                print(f"  Page {page}: {len(current_data)} scores")
                
                if len(current_data) < 100:
                    break
                page += 1
            
            print(f"Total {mode_names[mode]} scores: {len([d for d in all_data if d.get('play_mode') == mode])}")
    else:
        # Single mode servers
        page = 1
        while page <= 50:
            api_url = build_api_url(server_config, server_config["scores_endpoint"], 
                                  username, 100, page, user_id)
            
            response = fetch_api_data(api_url, access_token)
            if response.status_code != 200:
                print(f"Error {response.status_code}: {response.text}")
                break
            
            data = response.json()
            current_data = data if isinstance(data, list) else data.get("data", data.get("scores", []))
            
            if not current_data:
                break
            
            all_data.extend(current_data)
            print(f"Page {page}: {len(current_data)} scores")
            
            if len(current_data) < 100:
                break
            page += 1
    
    return all_data


def get_username_display(username, user_id, server_id):
    server_config = SERVERS[server_id]
    target_user = username if username else user_id
    
    if server_config.get("auth_required"):
        access_token = get_access_token()
        if access_token:
            bancho_user_id, actual_username = get_user_id(target_user, access_token)
            return actual_username if actual_username else target_user
    
    # For non-auth servers, try to fetch user data
    user_url = build_api_url(server_config, server_config["user_endpoint"], target_user)
    response = fetch_api_data(user_url)
    
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("username", user_data.get("name", target_user))
    
    return target_user


def seconds_to_mmss(seconds):
    try:
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"
    except:
        return "00:00"


def get_mode_name(mode):
    """Convert numeric mode to string name"""
    mode_map = {0: "osu", 1: "taiko", 2: "fruits", 3: "mania"}
    if isinstance(mode, str):
        return mode
    return mode_map.get(int(mode) if str(mode).isdigit() else 0, "osu")


def parse_and_export(username, user_id, server_id):
    with open(OUTPUT_JSON, "r") as infile:
        data = json.load(infile)
    
    unique_ids = set()
    csv_rows = []
    
    username_display = get_username_display(username, user_id, server_id)
    target_user = username if username else user_id
    header_title = f"Beatmaps Played by {username_display} in {SERVERS[server_id]['name']}"
    headers = [
        "Index", "Username", "User ID", "Beatmapset Name", "Beatmapset ID",
        "Beatmapset Artist", "Beatmap Creator", "Beatmap Difficulty Title",
        "Beatmap Difficulty ID", "Mode", "Status", "Length",
        "Star Rating", "Retry Count", "Download Link"
    ]
    csv_rows.extend([[header_title], headers])
    
    for idx, item in enumerate(data, start=1):
        beatmap = item.get("beatmap", {})
        beatmapset = item.get("beatmapset", {})
        
        # Extract data with unified fallback system
        beatmapset_id = beatmap.get("beatmapset_id", "N/A")
        beatmap_difficulty_id = beatmap.get("beatmap_id", beatmap.get("id", "N/A"))
        mode_raw = beatmap.get("play_mode", beatmap.get("mode", item.get("play_mode", "N/A")))
        mode = get_mode_name(mode_raw)
        total_length_sec = beatmap.get("hit_length", beatmap.get("total_length", 0))
        star_rating = beatmap.get("difficulty2", beatmap.get("difficulty_rating", beatmap.get("difficulty", "N/A")))
        retry_count = item.get("count", "N/A")
        
        # Handle different title/artist formats
        if beatmapset.get("title"):  # Bancho format
            beatmapset_name = beatmapset["title"]
            beatmapset_artist = beatmapset.get("artist", "N/A")
            beatmap_creator = beatmapset.get("creator", "N/A")
            beatmap_difficulty_title = beatmap.get("version", "N/A")
            status = beatmap.get("status", "N/A")
        else:  # Private server format
            song_name = beatmap.get("song_name", "N/A")
            if " - " in song_name and " [" in song_name:
                artist_title = song_name.split(" [")[0]
                if " - " in artist_title:
                    beatmapset_artist, beatmapset_name = artist_title.split(" - ", 1)
                    beatmap_difficulty_title = song_name.split(" [")[1].rstrip("]")
                else:
                    beatmapset_artist = "N/A"
                    beatmapset_name = artist_title
                    beatmap_difficulty_title = song_name.split(" [")[1].rstrip("]") if " [" in song_name else "N/A"
            else:
                beatmapset_artist = "N/A"
                beatmapset_name = song_name
                beatmap_difficulty_title = "N/A"
            beatmap_creator = "N/A"
            status = "ranked" if beatmap.get("ranked", 0) > 0 else "unranked"
        
        unique_ids.add(str(beatmapset_id))
        
        csv_rows.append([
            idx, username_display, target_user, beatmapset_name, beatmapset_id,
            beatmapset_artist, beatmap_creator, beatmap_difficulty_title,
            beatmap_difficulty_id, mode, status, 
            seconds_to_mmss(total_length_sec), star_rating,
            retry_count, f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}#{mode}/{beatmap_difficulty_id}"
        ])
    
    # Export files
    with open(ID_TXT, "w") as idfile:
        idfile.write('\n'.join(sorted(unique_ids)) + '\n')
    print(f"Unique beatmapset IDs exported to {ID_TXT}")
    
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvfile:
        csv.writer(csvfile).writerows(csv_rows)
    print(f"CSV exported to {CSV_FILE}")


def main():
    args = parse_args()
    
    data = fetch_server_data(args.username, args.user_id, args.server)
    if data is None:
        print("No data fetched. Exiting.")
        return
    
    with open(OUTPUT_JSON, "w") as outfile:
        json.dump(data, outfile, indent=4)
    print(f"Data exported to {OUTPUT_JSON} - Total: {len(data)} scores")
    
    parse_and_export(args.username, args.user_id, args.server)


if __name__ == "__main__":
    main()
