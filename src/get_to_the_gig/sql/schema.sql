CREATE TABLE IF NOT EXISTS
    venues (
        venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ref TEXT UNIQUE NOT NULL,
        street TEXT,
        city TEXT,
        state TEXT,
        zip_code INTEGER,
        url TEXT NOT NULL,
        calendar_url TEXT NOT NULL,
        date_added TIMESTAMP NOT NULL
    );

CREATE TABLE IF NOT EXISTS
    events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        venue_id INTEGER REFERENCES Venues (venue_id) ON DELETE RESTRICT ON UPDATE CASCADE,
        title TEXT NOT NULL,
        date TIMESTAMP,
        acts TEXT,
        price TEXT,
        url TEXT,
        ticket_url TEXT,
        act_urls TEXT,
        info TEXT,
        age_restriction TEXT,
        date_added TIMESTAMP NOT NULL
    );