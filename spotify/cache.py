from cachetools import TTLCache

ARTIST_ID_CACHE = TTLCache(maxsize=5_000, ttl=86400)
TOP_TRACK_CACHE = TTLCache(maxsize=10_000, ttl=3600)