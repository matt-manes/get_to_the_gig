import gruel
from pathier import Pathier
from typing_extensions import Any, Sequence, override

from get_to_the_gig import models
from get_to_the_gig.gigbased import Gigbased

root = Pathier(__file__).parent


# TODO: add methods for dead and resurrected events
class GigGruel(gruel.Gruel):
    """Base class for event scrapers."""

    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["log_dir"] = root / "logs"
        super().__init__(*args, **kwargs)
        self._venue: models.Venue = self._get_venue()
        self.already_added_events: list[models.Event] = []
        self.newly_added_events: list[models.Event] = []

    @property
    def venue(self) -> models.Venue:
        """The venue model for this scraper."""
        return self._venue

    def _get_venue(self) -> models.Venue:
        with Gigbased() as db:
            return db.get_venues(where=f"ref = '{self.name}'")[0]

    def get_existing_listings(self) -> list[models.Event]:
        """Return a list of events from the database for this venue."""
        with Gigbased() as db:
            return db.get_events(where=f"venue_id = {self.venue.venue_id}")

    def new_event(self) -> models.Event:
        """Returns a `models.Event` instance populated only with this venue, the current datetime, and an `event_id` of -1."""
        return models.Event.new(self.venue)

    @override
    def get_source(self) -> gruel.Response:
        """Defaults to fetching `self.venue.calendar_url`."""
        return self.request(self.venue.calendar_url)

    def add_event_to_db(self, event: models.Event) -> None:
        try:
            with Gigbased() as db:
                db.add_event(event)
                self.newly_added_events.append(event)
        except Exception as e:
            self.logger.error("Error adding event to database.")

    @override
    def store_items(self, items: Sequence[models.Event | None]) -> None:
        existing_listings = self.get_existing_listings()
        for event in items:
            if not event:
                continue
            event.trim()
            if event in existing_listings:
                self.already_added_events.append(event)
            else:
                self.add_event_to_db(event)
