from db.queries import get_random_festival_year_id, get_random_artists_for_year

def generate_random_artists():
    festival_year_id = get_random_festival_year_id()
    random_artists = get_random_artists_for_year(festival_year_id)
    return random_artists