import logging
from datetime import datetime, timedelta
from functools import cached_property, wraps
from typing import Iterable
import nocamel
import requests
from bs4 import BeautifulSoup
from noiftimer import Timer
from pathier import Pathier
from whosyouragent import get_agent

root = Pathier(__file__).parent
root.parent.add_to_PATH()
import models
from config import Config
from gigbased import GigBased


class GigScraper:
    """Base class for scrapers."""

    def __init__(self):
        self.init_logger()
        self.timer = Timer()
        self.config = Config.load(root.parent / "config.toml")
        self.add_count = 0
        self.fail_count = 0

    @property
    def name(self) -> str:
        """This scraper's name. Equivalent to it's `ref_name` in the database."""
        return Pathier(__file__).stem

    @cached_property
    def venue(self) -> models.Venue:
        """The venue model for this scraper."""
        with GigBased() as db:
            return db.get_venue(nocamel.convert_string(self.name).lower())

    def add_event(self, event: models.Event):
        """Add `event` to database or update the entry if it appears to already be in the database."""
        event.venue = self.venue.name
        event = self.check_event_year(event)
        event.clean()
        # ADD detections for event already existing
        with GigBased() as db:
            db.add_event(event)
        self.add_count += 1

    @staticmethod
    def as_soup(response: requests.Response) -> BeautifulSoup:
        """Return `response.text` as a `BeautifulSoup` object."""
        return BeautifulSoup(response.text, "html.parser")

    def check_event_year(self, event: models.Event) -> models.Event:
        """If the event date looks to be more than 30 days in the past, increase the year by 1.

        Some venues don't list the year, so if the event looks to be in the past, it's probably next year.

        e.g. it's currently December and the event is in January,
        but no year listed may result in a datetime for January of this year instead of next year.

        Use of this function assumes the venue removes previous events from their website within 30 days after the event."""
        if (datetime.now() - event.date).days > 30:
            event.date = event.date.replace(year=event.date.year + 1)
        return event

    def event_fail(self, event: models.Event):
        """Call when an exception occurs while scraping a given event.
        Will log the error with a dump of `event` (scraper code and non present values can help determine culprit)
        and increment `self.fail_count`."""
        marker = "'/////////////// EVENT DUMP ///////////////'"
        event.clean()
        self.logger.exception(f"\n{marker}\n\n{event.dump()}\n\n{marker}")
        self.fail_count += 1

    def get_calendar(self) -> requests.Response:
        """Make a request to this venue's calendar url."""
        return self.get_page(self.venue.calendar_url)

    @staticmethod
    def get_page(url: str, headers: dict[str, str] = {}) -> requests.Response:
        """Request `url` and return the `requests.Response` object."""
        return requests.get(url, headers=get_agent(True) | headers)

    def get_squarespace_calendar(self, collection_id: str) -> Iterable[dict]:
        """Generator that yields a dictionary of event details for venues
        using the squarespace endpoint `{venue_website}/api/open/GetItemsByMonth`.

        `collection_id` should be rendered somewhere in the calendar HTML."""
        date = datetime.now()
        counter = 0
        while True:
            month_year = f"{date:%m-%Y}"
            url = f"{self.venue.website}/api/open/GetItemsByMonth?month={month_year}&collectionId={collection_id}"
            response = self.get_page(url)
            # Length of 2 means no content
            if len(response.content) == 2 or counter >= 12:
                break
            yield response.json()
            date += timedelta(weeks=4)
            counter += 1

    def init_logger(self):
        log_dir = root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.venue.ref_name)
        if not self.logger.hasHandlers():
            handler = logging.FileHandler(
                (log_dir / self.venue.ref_name).with_suffix(".log"), encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter(
                    "{levelname}|-|{asctime}|-|{message}",
                    style="{",
                    datefmt="%m/%d/%Y %I:%M:%S %p",
                )
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    # Seat |========================================== Chores ==========================================|

    def chores(scrape):
        """Chores to do before and after running `self.scrape()`."""

        @wraps(scrape)
        def inner(self):
            self.prescrape_chores()
            scrape(self)
            self.postscrape_chores()

        return inner

    def postscrape_chores(self):
        """Chores to do after scraping the venue."""
        self.timer.stop()
        self.logger.info(
            f"Scrape completed in {self.timer.elapsed_str} with {self.add_count} successes and {self.fail_count} failures."
        )

    def prescrape_chores(self):
        """Chores to do before scraping the venue."""
        if self.config.backup_before_scrape:
            Pathier(self.config.dbpath).backup()
        with GigBased() as db:
            # May be temporary until a better way of detecting whether an event is updated or a duplicate.
            # Dropping all of them first is easier, but renders the "date_added" field meaningless.
            if self.config.drop_all_events:
                db.delete("events", {"venue": self.venue.name})
            if self.config.update_in_the_future:
                db.update_in_the_future()
            if self.config.drop_future_events:
                db.drop_future_events(self.venue)
        self.timer.start()
        self.logger.info("Scrape started.")

    # Seat |====================================== Overrides ======================================|

    def get_events(self) -> list[dict | BeautifulSoup]:
        """Fetch calendar and prepare data."""
        raise NotImplementedError

    def parse_event(self, listing: dict | BeautifulSoup) -> models.Event | None:
        """Parse a singular event from either a dictionary
        or BeautifulSoup object depending on the venue website.

        Basic template:
        >>> try:
        >>>     event = models.Event.new()
        >>>     # Populate `event` from `listing`.
        >>> except Exception:
        >>>     # This will log the exception and current contents of `event`
        >>>     self.event_fail(event)
        >>>     return None
        >>> return event"""
        raise NotImplementedError

    @chores
    def scrape(self):
        """Override this in a specific Venue's subclass and decorate with `GigScraper.chores`."""
        raise NotImplementedError
