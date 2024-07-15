import dacite
from databased import Databased
from pathier import Pathier, Pathish
from typing_extensions import Any, Callable

from . import models

root = Pathier(__file__).parent


# TODO : way of checking if an event is pre-existing besides url
class Gigbased(Databased):
    def __init__(self, dbpath: Pathish = root / "data" / "get_to_the_gig.db"):
        super().__init__(dbpath, log_dir="logs")

    # Seat ====================================================================

    def add_event(self, event: models.Event) -> int:
        """Add an event to the database.

        Returns `1` if successful.

        * NOTE: `event.event_id` will be ignored and auto-assigned by the database."""
        return self.insert(
            "events",
            (
                "venue_id",
                "title",
                "date",
                "acts",
                "price",
                "url",
                "ticket_url",
                "act_urls",
                "info",
                "age_restriction",
                "date_added",
            ),
            [
                (
                    event.venue.venue_id,
                    event.title,
                    event.date,
                    event.acts,
                    event.price,
                    event.url,
                    event.ticket_url,
                    event.act_urls,
                    event.info,
                    event.age_restriction,
                    event.date_added,
                )
            ],
        )

    def add_venue(self, venue: models.Venue) -> int:
        """Add a venue to the database.

        Returns `True` if successful."""
        return self.insert(
            "venues",
            (
                "name",
                "ref",
                "street",
                "city",
                "state",
                "zip_code",
                "url",
                "calendar_url",
                "date_added",
            ),
            [
                (
                    venue.name,
                    venue.ref,
                    venue.street,
                    venue.city,
                    venue.state,
                    venue.zip_code,
                    venue.url,
                    venue.calendar_url,
                    venue.date_added,
                )
            ],
        )

    def get_venues(self, *args: Any, **kwargs: Any) -> list[models.Venue]:
        """Returns a list of `models.Venue` objects from the `venues` table.

        `*args` and `**kwargs` can be anything accepted by `Databased.select()` except `table`:

        `columns: Iterable[str] = ["*"]`
        `joins: Iterable[str] | None = None`
        `where: str | None = None`
        `group_by: str | None = None`
        `having: str | None = None`
        `order_by: str | None = None`
        `limit: int | str | None = None`
        `exclude_columns: Iterable[str] `
        """
        rows = self.select("venues", *args, **kwargs)
        return [dacite.from_dict(models.Venue, row) for row in rows]

    def get_events(self, *args: Any, **kwargs: Any) -> list[models.Event]:
        """Returns a list of `models.Event` objects from the `events` table.

        `*args` and `**kwargs` can be anything accepted by `Databased.select()` except `table`:

        `columns: Iterable[str] = ["*"]`
        `joins: Iterable[str] | None = None`
        `where: str | None = None`
        `group_by: str | None = None`
        `having: str | None = None`
        `order_by: str | None = None`
        `limit: int | str | None = None`
        `exclude_columns: Iterable[str] `
        """
        rows = self.select("events", *args, **kwargs)
        events: list[models.Event] = []
        venue_cache: dict[int, models.Venue] = {}
        for row in rows:
            venue_id = row.pop("venue_id")
            if venue_id in venue_cache:
                venue = venue_cache[venue_id]
            else:
                venue = self.get_venues(where=f"venue_id = {venue_id}")[0]
                venue_cache[venue.venue_id] = venue
            row["venue"] = venue
            events.append(dacite.from_dict(models.Event, row))
        return events

    def event_exists(self, url: str) -> bool:
        """Returns `True` if an event with the given `url` exists in the `events` table."""
        return self.count("events", where=f"url LIKE '{url}'") > 0

    def update_event(self, event: models.Event):
        """Update an event in the `events` table using `event` if it exists."""
        where = f"url = '{event.url}'"
        old_event = self.get_events(where=where)[0]
        old_value: Callable[[str], Any] = lambda col: getattr(old_event, col)
        new_value: Callable[[str], Any] = lambda col: getattr(event, col)
        # Handle change of venue separately since the field is another model
        if event.venue.venue_id != old_event.venue.venue_id:
            self.update("events", "venue_id", event.venue.venue_id, where=where)

        # Only update a column if the new value is different from the old
        for column in [
            column
            for column in self.get_columns("events")
            if column not in ["event_id", "venue_id"]
        ]:
            if old_value(column) != (updated_value := new_value(column)):
                self.update("events", column, updated_value, where=where)

    def upsert_event(self, event: models.Event):
        """Add `event` if it doesn't exist, if it does exist, update the entry."""
        if event.url and self.event_exists(event.url):
            self.update_event(event)
        else:
            self.add_event(event)
