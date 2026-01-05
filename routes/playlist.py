import os
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import RedirectResponse

from selection.selection import generate_random_artists

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


