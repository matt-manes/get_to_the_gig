CREATE VIEW IF NOT EXISTS
    events_view AS
SELECT
    event_id,
    events.venue_id,
    title,
    date,
    venues.name,
    acts,
    price,
    ticket_url,
    events.date_added,
    CASE
        WHEN CAST(JULIANDAY ('now') - JULIANDAY (date) AS INT) THEN 1
        ELSE 0
    END in_the_future
FROM
    events
    INNER JOIN venues ON events.venue_id = venues.venue_id;