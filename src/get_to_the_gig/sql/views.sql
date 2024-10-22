CREATE VIEW IF NOT EXISTS
    events_view AS
SELECT
    event_id AS eid,
    events.venue_id AS vid,
    title,
    date,
    venues.name AS venue,
    acts,
    price,
    ticket_url,
    events.date_added
FROM
    events
    INNER JOIN venues ON events.venue_id = venues.venue_id;

CREATE VIEW IF NOT EXISTS
    future_events AS
SELECT
    event_id AS eid,
    events.venue_id AS vid,
    title,
    date,
    venues.name AS venue,
    acts,
    price,
    ticket_url,
    events.date_added
FROM
    events
    INNER JOIN venues ON events.venue_id = venues.venue_id
WHERE
    CAST(JULIANDAY (date) - JULIANDAY ('now') AS INT) >= 0
ORDER BY
    date;

CREATE VIEW IF NOT EXISTS
    past_events AS
SELECT
    event_id AS eid,
    events.venue_id AS vid,
    title,
    date,
    venues.name AS venue,
    acts,
    price,
    ticket_url,
    events.date_added
FROM
    events
    INNER JOIN venues ON events.venue_id = venues.venue_id
WHERE
    CAST(JULIANDAY (date) - JULIANDAY ('now') AS INT) < 0
ORDER BY
    date;

CREATE VIEW IF NOT EXISTS
    today AS
SELECT
    event_id AS eid,
    events.venue_id AS vid,
    title,
    date,
    venues.name AS venue,
    acts,
    price,
    ticket_url,
    events.date_added
FROM
    events
    INNER JOIN venues ON events.venue_id = venues.venue_id
WHERE
    CAST(JULIANDAY (date) - JULIANDAY ('now') AS INT) = 0
    AND JULIANDAY (date) > JULIANDAY ('now')
    AND JULIANDAY (date) < JULIANDAY (date('now', '+1 day'))
ORDER BY
    date;