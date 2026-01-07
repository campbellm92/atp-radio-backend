import os, random
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from selection.selection import generate_random_artists
from spotify.track_resolver import resolve_artist_id, resolve_artist_to_track_uri

router = APIRouter()

TARGET_PLAYLIST_SIZE = 12
MAX_ATTEMPTS = 20
ALLOW_REPEATS_AFTER = MAX_ATTEMPTS // 2

@router.get("/artists")
def get_random_artists(request: Request):
    authenticated = bool(request.cookies.get("access_token"))
    if not authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")

    artists = generate_random_artists()
    if not artists:
        raise HTTPException(status_code=404, detail="No artists returned in response.")
    
    response = []
    for artist in artists:
        shape = {"id": artist[0], "name": artist[1]}
        response.append(shape)
    return response

@router.get("/play")
async def play(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    artists = generate_random_artists()
    if not artists:
        raise HTTPException(status_code=404, detail="No artists returned in response.")

    response = []
    attempts = 0
    seen_artists = set()
    

    while attempts < MAX_ATTEMPTS and len(response) < TARGET_PLAYLIST_SIZE:
        attempts += 1

        artist_id, artist_name = random.choice(artists)
        key = artist_name.lower().strip()

        if key in seen_artists and attempts < ALLOW_REPEATS_AFTER:
            continue
        seen_artists.add(key)

        spotify_artist_id = await resolve_artist_id(artist_name, access_token)
        if not spotify_artist_id:
            continue

        track_uri = await resolve_artist_to_track_uri(spotify_artist_id, access_token)
        if not track_uri:
            continue

        response.append({
            "artist_id": artist_id,
            "artist_name": artist_name,
            "track_uri": track_uri
        })

    return {
        "tracks": response,
        "attempts": attempts,
        "requested": TARGET_PLAYLIST_SIZE,
        "returned": len(response),
    }
