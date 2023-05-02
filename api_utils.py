import requests
import sys
from datetime import datetime, timedelta, date
#authorization
def get_access_token(client_id, client_secret):
    auth_url = "https://id.twitch.tv/oauth2/token"
    auth_payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    auth_response = requests.post(auth_url, params=auth_payload)
    if auth_response.status_code != 200:
        print("Error: Unable to fetch OAuth token.")
        sys.exit(1)
    return auth_response.json()["access_token"]

#get game ID for twitch API 
def get_game_id(game_name, client_id, access_token):
    game_name = game_name.lower()
    game_url = "https://api.twitch.tv/helix/games"
    game_params = {"name": game_name}
    game_headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    game_response = requests.get(game_url, params=game_params, headers=game_headers)
    if game_response.status_code != 200:
        print("Error: Unable to fetch game information.")
        sys.exit(1)
    return game_response.json()["data"][0]["id"]

#scrape top clips (currently set to 25)
def get_top_clips(game_id, client_id, access_token, language="en", limit=25):
    clips_url = "https://api.twitch.tv/helix/clips"
    one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    filtered_clips = []
    cursor = None

    while len(filtered_clips) < limit:
        clips_params = {
            "game_id": game_id,
            "first": 100,  # Request the maximum allowed number of clips
            "started_at": one_day_ago
        }
        if cursor:
            clips_params["after"] = cursor

        clips_headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        }
        clips_response = requests.get(clips_url, params=clips_params, headers=clips_headers)
        if clips_response.status_code != 200:
            print("Error: Unable to fetch top clips.")
            sys.exit(1)

        all_clips = clips_response.json()["data"]
        cursor = clips_response.json()["pagination"].get("cursor")

        for clip in all_clips:
            if clip['language'] == language:
                filtered_clips.append(clip)
                if len(filtered_clips) == limit:
                    break

        if not cursor:
            break

    return filtered_clips

#get twitch username
def get_broadcaster_login(broadcaster_id, client_id, access_token):
    user_url = "https://api.twitch.tv/helix/users"
    user_params = {"id": broadcaster_id}
    user_headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    user_response = requests.get(user_url, params=user_params, headers=user_headers)
    if user_response.status_code != 200:
        print("Error: Unable to fetch broadcaster information.")
        sys.exit(1)
    return user_response.json()["data"][0]["login"]