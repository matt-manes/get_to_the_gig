import gruel
from pathier import Pathier
from rich.console import Console
from typing_extensions import Any, Sequence, Type, override

from get_to_the_gig import models
from get_to_the_gig.event_parser import EventParser
from get_to_the_gig.gigbased import Gigbased

console = Console(style="deep_pink4")
root = Pathier(__file__).parent


# TODO: add methods for dead and resurrected events
class GigGruel(gruel.Gruel):
    """
    Base class for event scrapers.

    Subclasses need to implement:
        * `def get_parsable_items(self, source: gruel.Response) -> list[Tag]`
    """

    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["log_dir"] = root / "logs"
        super().__init__(*args, **kwargs)
        self._venue: models.Venue = self._get_venue()
        self.already_added_events: list[models.Event] = []
        self.newly_added_events: list[models.Event] = []
        self.test_mode = False

    @property
    def venue(self) -> models.Venue:
        """The venue model for this scraper."""
        return self._venue

    @property
    def event_parser(self) -> Type[EventParser]:
        return EventParser

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

    @override
    def parse_item(self, item: Any) -> models.Event:
        return self.event_parser(self.venue, item).parse()

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
            if self.test_mode:
                console.print()
                console.print(str(event))
            else:
                if event in existing_listings:
                    self.already_added_events.append(event)
                else:
                    self.add_event_to_db(event)
