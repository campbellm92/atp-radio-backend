import os
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import RedirectResponse

from selection.selection import generate_random_artists
from spotify.track_resolver import resolve_artist_id, resolve_artist_to_track_uri

router = APIRouter()

REDIRECT = os.environ["URI"] + "/login"

@router.get("/artists")
def get_random_artists(request: Request):
    authenticated = bool(request.cookies.get("access_token"))

    if not authenticated:
        return RedirectResponse(url=REDIRECT)

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
        return RedirectResponse(url=REDIRECT)
    
    authenticated = bool(request.cookies.get("access_token"))

    if not authenticated:
        return RedirectResponse(url=REDIRECT)

    artists = generate_random_artists()

    if not artists:
        raise HTTPException(status_code=404, detail="No artists returned in response.")

    response = []
    seen = set()

    for artist_id, artist_name in artists:
        key = artist_name.lower().strip()

        if key in seen:
            continue

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

    return response
