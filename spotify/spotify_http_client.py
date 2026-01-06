import httpx, asyncio

spotify_http_client: httpx.AsyncClient | None = None
spotify_semaphore = asyncio.Semaphore(5)


async def start_client():
    global spotify_http_client
    if spotify_http_client is None:
        spotify_http_client = httpx.AsyncClient(
            base_url="https://api.spotify.com/v1",
            timeout=5.0,
        )


async def stop_client():
    global spotify_http_client
    if spotify_http_client is not None:
        await spotify_http_client.aclose()
        spotify_http_client = None


def get_client() -> httpx.AsyncClient:
    if spotify_http_client is None:
        raise RuntimeError("Spotify HTTP client not initialised")
    return spotify_http_client
