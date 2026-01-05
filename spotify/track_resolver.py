import requests, random

def resolve_artist_id(artist_name, access_token):
    endpoint = "https://api.spotify.com/v1/search"

    headers = {"Authorization": f"Bearer {access_token}"}

    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    
    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code != 200:
        print("Spotify error:", response.text)
        return
    
    data = response.json()

    items = data["artists"]["items"]
    if not items:
        return None

    artist_id = items[0]["id"]

    print(response.status_code)
    print(response.json())
    print(artist_id)
    return artist_id



def resolve_artist_to_track_uri(artist_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"

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
        return None

    track = random.choice(tracks)
    return track["uri"]






