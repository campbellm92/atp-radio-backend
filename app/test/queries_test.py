# python3 -m app.tests.test_db
from db.queries import get_random_festival_year_id, get_random_artists_for_year

year_id = get_random_festival_year_id()
print("Year ID:", year_id)

artists = get_random_artists_for_year(year_id, limit=5)
print("Artists:", artists)