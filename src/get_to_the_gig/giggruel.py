import gruel
import models
from gigbased import Gigbased
from pathier import Pathier
from typing_extensions import Any, Sequence, override

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
        self.new_events: list[models.Event] = []

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
                try:
                    with Gigbased() as db:
                        db.add_event(event)
                        self.new_events.append(event)
                except Exception as e:
                    self.logger.error("Error adding event to database.")


# class GigGruel(gruel.Gruel):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.config = Config.load(root.parent / "config.toml")
#        self.store_item = self.add_event
#
#    @property
#    def name(self) -> str:
#        return Pathier(inspect.getsourcefile(type(self))).stem
#
#    @cached_property
#    def venue(self) -> models.Venue:
#        """The venue model for this scraper."""
#        with GigBased() as db:
#            return db.get_venue(nocamel.convert_string(self.name).lower())
#
#    def get_calendar(self) -> requests.Response:
#        """Make a request to this venue's calendar url."""
#        return self.request(self.venue.calendar_url)
#
#    def get_squarespace_calendar(self, collection_id: str) -> Iterable[dict]:
#        """Generator that yields a dictionary of event details for venues
#        using the squarespace endpoint `{venue_website}/api/open/GetItemsByMonth`.
#
#        `collection_id` should be rendered somewhere in the calendar HTML."""
#        date = datetime.now()
#        counter = 0
#        while True:
#            month_year = f"{date:%m-%Y}"
#            url = f"{self.venue.url}/api/open/GetItemsByMonth?month={month_year}&collectionId={collection_id}"
#            response = self.request(url)
#            # Length of 2 means no content
#            if len(response.content) == 2 or counter >= 12:
#                break
#            yield response.json()
#            date += timedelta(weeks=4)
#            counter += 1
#
#    def get_squarespace_events(self, collection_id: str) -> list[dict]:
#        """Effectively exhaust and flatten `self.get_squarespace_calendar()`.
#
#        `collection_id` should be rendered somewhere in the calendar HTML."""
#        return [
#            event
#            for month in self.get_squarespace_calendar(collection_id)
#            for event in month
#        ]
#
#    def add_event(self, event: models.Event):
#        """Add `event` to database or update the entry if it appears to already be in the database."""
#        event.venue = self.venue.name
#        event = self.check_event_year(event)
#        event.clean()
#        if event.date < datetime.today():
#            event.in_the_future = False
#        # ADD detections for event already existing
#        with GigBased() as db:
#            db.add_event(event)
#        self.success_count += 1
#
#    def check_event_year(self, event: models.Event) -> models.Event:
#        """If the event date looks to be more than 30 days in the past, increase the year by 1.
#
#        Some venues don't list the year, so if the event looks to be in the past, it's probably next year.
#
#        e.g. it's currently December and the event is in January,
#        but no year listed may result in a datetime for January of this year instead of next year.
#
#        Use of this function assumes the venue removes previous events from their website within 30 days after the event.
#        """
#        if (datetime.now() - event.date).days > 30:
#            event.date = event.date.replace(year=event.date.year + 1)
#        return event
#
#    def event_fail(self, event: models.Event):
#        """Call when an exception occurs while scraping a given event.
#        Will log the error with a dump of `event` (scraper code and non present values can help determine culprit)
#        and increment `self.fail_count`."""
#        marker = "'/////////////// EVENT DUMP ///////////////'"
#        event.clean()
#        self.logger.exception(f"\n{marker}\n\n{event.dump()}\n\n{marker}")
#        self.fail_count += 1
#
#    @property
#    def last_log(self) -> str:
#        return (root.parent / "logs" / f"{self.name}.log").split()[-1]
#
#    def clean(self, text: str) -> str:
#        """Strip ` \\n\\r\\t` and remove `"` from `text`."""
#        return text.strip(" \n\t\r").replace('"', "")
#
#    def prescrape_chores(self):
#        super().prescrape_chores()
#        if self.config.backup_before_scrape:
#            Pathier(self.config.dbpath).backup()
#        with GigBased() as db:
#            # May be temporary until a better way of detecting whether an event is updated or a duplicate.
#            # Dropping all of them first is easier, but renders the "date_added" field meaningless.
#            if self.config.drop_all_events:
#                db.delete("events", f"venue = '{self.venue.name}'")
#            if self.config.update_in_the_future:
#                db.update_in_the_future()
#            if self.config.drop_future_events:
#                db.drop_future_events(self.venue)
#
#    def get_parsable_items(self) -> list[ParsableItem]:
#        """Get relevant webpages and extract raw data that needs to be parsed.
#
#        e.g. first 10 results for an endpoint that returns json content
#        >>> return self.get_page(some_url).json()[:10]"""
#        raise NotImplementedError
#
#    def parse_item(self, item: ParsableItem) -> Any:
#        """Parse `item` and return parsed data.
#
#        e.g.
#        >>> try:
#        >>>     parsed = {}
#        >>>     parsed["thing1"] = item["element"].split()[0]
#        >>>     self.successes += 1
#        >>>     return parsed
#        >>> except Exception:
#        >>>     self.logger.exception("message")
#        >>>     self.failures += 1
#        >>>     return None"""
#        raise NotImplementedError
#
#    # def store_item(self, item: Any):
#    #    """Store `item`."""
#    #    raise NotImplementedError
