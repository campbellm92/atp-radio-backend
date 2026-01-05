import os
from dotenv import load_dotenv

from spotify.track_resolver import resolve_artist_id, resolve_artist_to_track_uri

load_dotenv()
ACCESS_TOKEN = os.environ["TEST_ACCESS_TOKEN"]

artist_name = "The Cleaners from Venus"

artist_id = resolve_artist_id(artist_name, ACCESS_TOKEN)
print("Artist ID:", artist_id)

if artist_id:
    track_uri = resolve_artist_to_track_uri(artist_id, ACCESS_TOKEN)
    print("Track URI:", track_uri)