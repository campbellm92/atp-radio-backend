import os
import sqlite3

DB_PATH = os.path.join("db", "atp.sqlite")

def get_db():
    return sqlite3.connect(DB_PATH)

def get_random_festival_year_id(limit = 1):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM festival_years ORDER BY RANDOM() LIMIT ?", (limit,))
    row = cur.fetchone()
    conn.close()
    return row[0]

def get_random_artists_for_year(festival_year_id, limit = 10):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
    """
    SELECT DISTINCT artists.id, artists.name
    FROM artists
    JOIN event_artists ON artists.id = event_artists.artist_id
    JOIN events ON events.id = event_artists.event_id
    WHERE events.festival_year_id = ?
    ORDER BY RANDOM()
    LIMIT ?
    """, (festival_year_id, limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
