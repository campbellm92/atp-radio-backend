import requests, random

from spotify.cache import ARTIST_ID_CACHE, TOP_TRACK_CACHE

def resolve_artist_id(artist_name, access_token):
    key = artist_name.lower().strip()

    if key in ARTIST_ID_CACHE:
        return ARTIST_ID_CACHE[key]

    endpoint = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    
    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code != 200:
        ARTIST_ID_CACHE[key] = None
        return None
    
    data = response.json()

    items = data["artists"]["items"]
    if not items:
        ARTIST_ID_CACHE[key] = None
        return None

    artist_id = items[0]["id"]
    ARTIST_ID_CACHE[key] = artist_id

    return artist_id



def resolve_artist_to_track_uri(artist_id, access_token):
    if artist_id in TOP_TRACK_CACHE:
        return TOP_TRACK_CACHE[artist_id]

    endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "market": "US"
    }

    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code != 200:
        print("Spotify top-tracks error:", response.text)
        return None

    data = response.json()
    tracks = data.get("tracks", [])

    if not tracks:
        TOP_TRACK_CACHE[artist_id] = None
        return None

    uri = random.choice(tracks)["uri"]
    TOP_TRACK_CACHE[artist_id] = uri
    return uri






