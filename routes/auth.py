import os, secrets, string, hashlib, base64, requests
from dotenv import load_dotenv
from urllib.parse import urlencode
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import RedirectResponse

load_dotenv()

router = APIRouter()

CLIENT_ID = os.environ["CLIENT_ID"]
STATE_KEY = "spotify_auth_state"
CODE_VERIFIER_KEY = "spotify_code_verifier"
URI = os.environ["URI"]
REDIRECT_URI = URI + "/callback"

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

@router.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

@router.get("/login")
def handle_login( response: Response):
    client_id = CLIENT_ID
    response_type = "code"
    redirect_uri = REDIRECT_URI
    scope = "user-read-private user-read-email"
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
    response.set_cookie(key=STATE_KEY, value=state_string, httponly=True, samesite="lax")
    response.set_cookie(key=CODE_VERIFIER_KEY, value=code_verifier, httponly=True, samesite="lax")

    return response

@router.get("/callback")
async def handle_callback(request: Request, response: Response):
    client_id = CLIENT_ID
    grant_type = "authorization_code"
    spotify_code = request.query_params.get("code")
    redirect_uri = REDIRECT_URI
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

    api_response = requests.post(token_endpoint, data=params)
    print(api_response.status_code, api_response.text)

    if api_response.status_code == 200:
        result = api_response.json()
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]

        response = RedirectResponse(url=URI)
        response.delete_cookie(STATE_KEY)
        response.delete_cookie(CODE_VERIFIER_KEY)
        response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax")
    else:
        raise HTTPException(status_code=api_response.status_code, detail="Token exchange failed.")

    return response

@router.get("/refresh_token")
def refresh_token_route(request: Request, response: Response):
    grant_type = "refresh_token"
    refresh_token = request.cookies.get("refresh_token")
    refresh_endpoint = "https://accounts.spotify.com/api/token"
    client_id = CLIENT_ID
 
    params = {
        "grant_type": grant_type,
        "refresh_token": refresh_token,
        "client_id": client_id 
    }

    api_response = requests.post(refresh_endpoint, data=params)
    print(api_response.status_code, api_response.text)

    if api_response.status_code == 200:
        result = api_response.json()
        access_token = result["access_token"]
        refresh_token = result.get("refresh_token", refresh_token)
        if refresh_token in result:
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax")
    else: 
        raise HTTPException(status_code=api_response.status_code, detail="Token refresh failed.")
    
    return {"access_token": access_token}