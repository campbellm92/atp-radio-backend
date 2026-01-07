from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import auth, playlist

from spotify.spotify_http_client import start_client, stop_client

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(playlist.router)

@app.get("/")
def root():
    return {"message": "API Radio playlist generator API."}


@app.on_event("startup")
async def startup():
    await start_client()


@app.on_event("shutdown")
async def shutdown():
    await stop_client()