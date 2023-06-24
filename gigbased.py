from datetime import datetime

import dacite
from databased import DataBased

import models


class GigBased(DataBased):
    def __init__(self, dbpath="getToTheGig.db"):
        super().__init__(dbpath)
        self.create_tables()

    def add_event(self, event: models.Event) -> bool:
        """Add an event to the database.

        Returns `True` if successful."""
        return self.add_row(
            "events",
            (
                event.venue.name if type(event.venue) == models.Venue else event.venue,
                event.title,
                event.date,
                event.acts,
                event.price,
                event.event_url,
                event.ticket_url,
                event.act_urls,
                event.info,
                event.age_restriction,
                event.date_added,
                event.genres,
                event.in_the_future,
            ),
            (
                "venue",
                "title",
                "date",
                "acts",
                "price",
                "event_url",
                "ticket_url",
                "act_urls",
                "info",
                "age_restriction",
                "date_added",
                "genres",
                "in_the_future",
            ),
        )

    def add_venue(self, venue: models.Venue) -> bool:
        """Add a venue to the database.

        Returns `True` if successful."""
        return self.add_row(
            "venues",
            [
                venue.name,
                venue.address.street,
                venue.address.city,
                venue.address.state,
                venue.address.zip_code,
                venue.website,
                venue.calendar_url,
                venue.ref_name,
                venue.date_added,
            ],
            [
                "name",
                "street",
                "city",
                "state",
                "zip_code",
                "website",
                "calendar_url",
                "ref_name",
                "date_added",
            ],
        )

    def create_events_table(self):
        self.create_table(
            "events",
            [
                "venue text",
                "title text",
                "date timestamp",
                "acts text",
                "price text",
                "event_url text",
                "ticket_url text",
                "act_urls text",
                "info text",
                "age_restriction text",
                "date_added timestamp",
                "genres text",
                "in_the_future int",
            ],
        )

    def create_tables(self):
        self.create_venues_table()
        self.create_events_table()

    def create_venues_table(self):
        self.create_table(
            "venues",
            [
                "name text unique",
                "street text",
                "city text",
                "state text",
                "zip_code text",
                "website text",
                "calendar_url text",
                "ref_name text",
                "date_added timestamp",
            ],
        )

    def drop_future_events(self, venue: models.Venue | None = None):
        """Delete events that haven't happened yet for `venue`.
        If `venue` is not given, the operation will occur on all venues.

        #### :Intention: Avoid adding duplicate events or needing to determine
        if the event to be added already exists but website information for it has changed.
        Ideally a backup of the database should be made first and this should be called after calling `self.update_in_the_future`."""
        if venue:
            self.delete("events", {"venue": venue.name, "in_the_future": 1})
        else:
            self.delete("events", {"in_the_future": 1})

    def get_events(self, *args, **kwargs) -> list[models.Event]:
        """Return a list of `Event` models.

        `*args` and `**kwargs` can be any parameters accepted by `self.get_rows()`, except `table`:

        * `match_criteria: list[tuple] | dict | None = None`
        * `exact_match: bool = True`
        * `sort_by_column: str | None = None`
        * `columns_to_return: list[str] | None = None`
        * `return_as_dataframe: bool = False`
        * `values_only: bool = False`
        * `order_by: str | None = None`
        * `limit: str | int | None = None`
        """
        rows = self.get_rows("events", *args, **kwargs)
        return [dacite.from_dict(models.Event, row) for row in rows]

    def get_venue(self, ref_name: str) -> models.Venue:
        """Return a `Venue` model given a venue's `ref_name`.
        Database connection will be closed after calling this function."""
        return dacite.from_dict(
            models.Venue, self.get_rows("venues", {"ref_name": ref_name})[0]
        )

    def get_venues(self, *args, **kwargs) -> list[models.Venue]:
        """Return a list of `Venue` models.

        `*args` and `**kwargs` can be any parameters accepted by `self.get_rows()`, except `table`:

        * `match_criteria: list[tuple] | dict | None = None`
        * `exact_match: bool = True`
        * `sort_by_column: str | None = None`
        * `columns_to_return: list[str] | None = None`
        * `return_as_dataframe: bool = False`
        * `values_only: bool = False`
        * `order_by: str | None = None`
        * `limit: str | int | None = None`
        """
        rows = self.get_rows("venues", *args, **kwargs)
        return [dacite.from_dict(models.Venue, row) for row in rows]

    def update_in_the_future(self):
        """Set `in_the_future` column in the events table to `0` for events that have already happened."""
        self.query(
            f"UPDATE events SET in_the_future = 0 WHERE date < '{datetime.now()}';"
        )

    def venue_in_database(self, venue: models.Venue) -> bool:
        """Returns True if `venue` is already in the database.
        Database connection will be closed after calling this function."""
        venue_dict = venue.flattened_dict
        venue_dict.pop("date_added")
        return self.count("venues", venue_dict) > 0


if __name__ == "__main__":
    # This is just to create the db file and/or tables if they don't exist
    GigBased()