import json, sqlite3

import json
import sqlite3

conn = sqlite3.connect("atp.sqlite")
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

with open("atp-lineups.json") as f:
    data = json.load(f)

for edition in data:
    year = edition["year"]
    location = edition["location"]

    cur.execute(
        """
        INSERT INTO festival_years (year, location)
        VALUES (?, ?)
        ON CONFLICT(year, location) DO NOTHING
        """,
        (year, location)
    )

    cur.execute(
        "SELECT id FROM festival_years WHERE year = ? AND location = ?",
        (year, location)
    )
    festival_year_id = cur.fetchone()[0]

    for event in edition["events"]:
        curator = event["curator"]

        cur.execute(
            """
            INSERT INTO events
            (festival_year_id, curator)
            VALUES (?, ?)
            ON CONFLICT(festival_year_id, curator)
            DO NOTHING
            """,
            (festival_year_id, curator)
        )

        cur.execute(
            """
            SELECT id FROM events
            WHERE festival_year_id = ?
              AND curator = ?
            """,
            (festival_year_id, curator)
        )
        event_id = cur.fetchone()[0]

        for artist_name in event["lineup"]:
            # --- artists ---
            cur.execute(
                """
                INSERT INTO artists (name)
                VALUES (?)
                ON CONFLICT(name) DO NOTHING
                """,
                (artist_name,)
            )

            cur.execute(
                "SELECT id FROM artists WHERE name = ?",
                (artist_name,)
            )
            artist_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO event_artists (event_id, artist_id)
                VALUES (?, ?)
                ON CONFLICT(event_id, artist_id) DO NOTHING
                """,
                (event_id, artist_id)
            )

conn.commit()
conn.close()
