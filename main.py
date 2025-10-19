import os
import secrets
import string
import hashlib
import base64
from urllib.parse import urlencode
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = os.environ["URI"] + "/callback"


def generate_state_string(length=20):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))

def generate_code_verifier(length=128):
    characters = string.ascii_letters + string.digits + "-._~"
    return "".join(secrets.choice(characters) for _ in range(length))

def generate_pkce(code_verifier: str) -> str:
    sha256_hash = hashlib.sha256(code_verifier.encode("ut-8")).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")
    return code_challenge

@app.get("/login")
def handle_login( response: Response):
    client_id = CLIENT_ID
    response_type = "code"
    redirect_uri = REDIRECT_URI
    scope = "user-read-private user-read-email"
    state_string = generate_state_string()
    code_challenge_method = "S256"
    code_verifier = generate_code_verifier()
    code_challenge = generate_pkce(code_verifier)
    
    response.set_cookie(key="code_verifier", value=code_verifier)
    response.set_cookie(key="oauth_state", value=state_string)

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

    return response