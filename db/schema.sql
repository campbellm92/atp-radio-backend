PRAGMA foreign_keys = ON;

CREATE TABLE festival_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    festival_year_id INTEGER NOT NULL,
    curator TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (festival_year_id) REFERENCES festival_years(id)
);

CREATE TABLE artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE event_artists (
    event_id INTEGER NOT NULL,
    artist_id INTEGER NOT NULL,
    PRIMARY KEY (event_id, artist_id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (artist_id) REFERENCES artists(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_festival_year ON festival_years (year, location);

CREATE UNIQUE INDEX IF NOT EXISTS uniq_event ON events (festival_year_id, curator, start_date, end_date);