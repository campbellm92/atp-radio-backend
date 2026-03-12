import os, secrets, string, hashlib, base64
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.spotify.spotify_http_client import get_client, spotify_semaphore

# config --------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env", override=True)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

CLIENT_ID = os.environ["CLIENT_ID"]
STATE_KEY = "spotify_auth_state"
CODE_VERIFIER_KEY = "spotify_code_verifier"

# helpers --------------------------------------------------------------
def generate_state_string(length=20):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))

def generate_code_verifier(length=128):
    characters = string.ascii_letters + string.digits + "-._~"
    return "".join(secrets.choice(characters) for _ in range(length))

def generate_pkce(code_verifier: str) -> str:
    sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")
    return code_challenge

async def refresh_access_token(refresh_token: str):
    spotify_http_client = get_client()
    refresh_endpoint = "https://accounts.spotify.com/api/token"

    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID
    }

    async with spotify_semaphore:
        api_response = await spotify_http_client.post(refresh_endpoint, data=params)

    if api_response.status_code != 200:
        raise HTTPException(
            status_code=api_response.status_code,
            detail="Token refresh failed"
        )

    result = api_response.json()

    return {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token")
    }

# schemas --------------------------------------------------------------
class AuthStatusOut(BaseModel):
    authenticated: bool

class SpotifyTokenOut(BaseModel):
    access_token: str

# routers ---------------------------------------------------------------

router = APIRouter()

@router.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

@router.get("/status", response_model=AuthStatusOut)
def auth_status(request: Request):
    return {
        "authenticated": bool(request.cookies.get("access_token"))
    }

@router.get("/spotify-token", response_model=SpotifyTokenOut)
async def get_access_token(request: Request, response: Response):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    tokens = await refresh_access_token(refresh_token)

    new_access_token = tokens["access_token"]
    new_refresh_token = tokens.get("refresh_token", refresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=IS_PRODUCTION,
        domain=".mattdev.it" if IS_PRODUCTION else None
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=IS_PRODUCTION,
        domain=".mattdev.it" if IS_PRODUCTION else None
    )

    return {"access_token": new_access_token}

@router.get("/login")
def handle_login(request: Request, response: Response):
    redirect_uri = str(request.base_url) + "auth/callback"
    client_id = CLIENT_ID
    response_type = "code"
    scope = " ".join([
        "user-read-private",
        "user-read-email",
        "streaming",
        "user-read-playback-state",
        "user-modify-playback-state",
        "playlist-modify-private",
        "playlist-modify-public",
    ])
    state_string = generate_state_string()
    code_challenge_method = "S256"
    code_verifier = generate_code_verifier()
    code_challenge = generate_pkce(code_verifier)

    params = {
        "client_id": client_id,
        "response_type": response_type,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state_string,
        "code_challenge_method": code_challenge_method,
        "code_challenge": code_challenge,
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    response = RedirectResponse(url=auth_url)

    response.set_cookie(
        key=STATE_KEY, 
        value=state_string, 
        httponly=True, 
        samesite="lax", 
        secure=IS_PRODUCTION, 
        domain=".mattdev.it" if IS_PRODUCTION else None
    )
    response.set_cookie(
        key=CODE_VERIFIER_KEY, 
        value=code_verifier, 
        httponly=True, 
        samesite="lax",
        secure=IS_PRODUCTION, 
        domain=".mattdev.it" if IS_PRODUCTION else None
    )
    return response

@router.get("/callback")
async def handle_callback(request: Request, response: Response):
    spotify_http_client = get_client()
    redirect_uri = str(request.base_url) + "auth/callback"
    client_id = CLIENT_ID
    grant_type = "authorization_code"
    spotify_code = request.query_params.get("code")
    state = request.query_params.get("state")
    stored_state = request.cookies.get(STATE_KEY)
    code_verifier = request.cookies.get(CODE_VERIFIER_KEY)
    token_endpoint = "https://accounts.spotify.com/api/token"

    if not spotify_code or not state:
        raise HTTPException(status_code=400, detail="Missing authorization code or state.")

    if state == None or state != stored_state:
        raise HTTPException(status_code=400, detail="State key mismatch.")

    params = {
        "client_id": client_id,
        "grant_type": grant_type,
        "code": spotify_code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier
    }

    async with spotify_semaphore:
        api_response = await spotify_http_client.post(token_endpoint, data=params)
    print(api_response.status_code, api_response.text)

    if api_response.status_code == 200:
        result = api_response.json()
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
        frontend_redirect = (
            "http://127.0.0.1:5173/"
            if request.base_url.hostname == "127.0.0.1"
            else "https://atp-radio.mattdev.it/"
        )

        response = RedirectResponse(url=frontend_redirect, status_code=302)

        response.delete_cookie(STATE_KEY)
        response.delete_cookie(CODE_VERIFIER_KEY)
        
        response.set_cookie(
            key="access_token", 
            value=access_token, 
            httponly=True, 
            samesite="lax",
            secure=IS_PRODUCTION, 
            domain=".mattdev.it" if IS_PRODUCTION else None
        )
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token, 
            httponly=True, 
            samesite="lax",
            secure=IS_PRODUCTION, 
            domain=".mattdev.it" if IS_PRODUCTION else None
        )
    else:
        raise HTTPException(status_code=api_response.status_code, detail="Token exchange failed.")

    return response

@router.get("/logout")
def logout():
    api_response = RedirectResponse("/", status_code= 303)
    api_response.delete_cookie(
        "access_token",
        path="/",
        domain=".mattdev.it" if IS_PRODUCTION else None
    )

    api_response.delete_cookie(
        "refresh_token",
        path="/",
        domain=".mattdev.it" if IS_PRODUCTION else None
    )
    return api_response