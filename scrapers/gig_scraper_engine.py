import logging
from datetime import datetime, timedelta
from functools import cached_property
from typing import Iterable

import nocamel
import requests
from bs4 import BeautifulSoup, element
from databased import DataBased
from noiftimer import Timer
from pathier import Pathier
from whosyouragent import get_agent

root = Pathier(__file__).parent
(root.parent).add_to_PATH()
import models
from gigbased import GigBased


def clean_string(string: str) -> str:
    return string.strip(" \n\t\r").replace('"', "")


def get_text(element: element.Tag | element.NavigableString, clean: bool = True) -> str:
    """Returns the text from a BeautifulSoup element, if there is any.

    Using this keeps try/except blocks from cluttering up scraper code.

    If clean is True, then ' \n\t\r' will be stripped from the string.

    Returns an empty string if element.text is None."""
    try:
        return clean_string(element.text) if clean else element.text
    except:
        return ""


def get_page(url: str) -> requests.Response:
    return requests.get(url, headers={"User-Agent": get_agent()})


def get_soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(get_page(url).text, "html.parser")


class GigScraper:
    """Base class for scrapers."""

    def __init__(self):
        self.init_logger()
        self.timer = Timer().start()

    @cached_property
    def venue(self) -> models.Venue:
        """The venue model for this scraper."""
        with GigBased() as db:
            return db.get_venue(nocamel.convert_string(self.name).lower())

    @cached_property
    def name(self) -> str:
        """This scraper's class name."""
        return type(self).__name__

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

    @staticmethod
    def get_page(self, url: str, headers: dict[str, str] = {}) -> requests.Response:
        """Request `url` and return the `requests.Response` object."""
        return requests.get(url, headers=get_agent(True) | headers)

    def get_calendar(self) -> requests.Response:
        """Make a request to this venue's calendar url."""
        return self.get_page(self.venue.calendar_url)

    @staticmethod
    def as_soup(self, response: requests.Response) -> BeautifulSoup:
        """Return `response.text` as a `BeautifulSoup` object."""
        return BeautifulSoup(response.text, "html.parser")


class GigScraperOld:
    """Base class for show scrapers.

    __init__ needs to be overridden by
    calling Pathier(__file__) and passing it to
    super().__init__().

    e.g.

    def __init__(self):

        super().__init__(Pathier(__file__))"""

    def __init__(self, scraper_path: Pathier):
        self.scraper_path = scraper_path
        self.db = DataBased(self.scraper_path.parent.parent / "shows.db")
        self.init_logger()
        self.venue_info = self.db.get_rows(
            "venues", [("reference_name", self.scraper_path.stem)]
        )[0]
        self.db.close()
        self.timer = Timer()
        self.timer.start()
        self.today = datetime.now()
        self.date_added = self.today
        self.venue = self.venue_info["name"]
        self.scrape_successful = False
        self.reset_event_details()

    def init_logger(self):
        log_dir = self.scraper_path.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.scraper_path.stem)
        if not self.logger.hasHandlers():
            handler = logging.FileHandler(
                (log_dir / self.scraper_path.stem).with_suffix(".log"), encoding="utf-8"
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

    def reset_event_details(self):
        self.event_date = ""
        self.title = ""
        self.acts = ""
        self.price = ""
        self.event_link = ""
        self.act_links = ""
        self.info = ""
        self.genres = ""
        self.in_the_future = 1

    def clean_strings(self):
        self.title = clean_string(self.title)
        self.acts = clean_string(self.acts)
        self.price = clean_string(self.price)
        self.event_link = clean_string(self.event_link)
        self.act_links = clean_string(self.act_links)
        self.info = clean_string(self.info)
        self.genres = clean_string(self.genres)

    def add_event(self):
        """Add event to database.

        If an entry with the same date and venue already exists,
        assumes it is the same event and updates the current entry
        with any new values (line up change, ticket price etc.)"""
        self.clean_strings()
        if (self.event_date - self.today).days < 0:
            self.in_the_future = 0
        event_details = (
            self.event_date,
            self.venue,
            self.title,
            self.acts,
            self.price,
            self.event_link,
            self.act_links,
            self.info,
            self.date_added,
            self.genres,
            self.in_the_future,
        )
        columns = self.db.get_column_names("events")
        self.db.close()
        identifier = [("venue", self.venue), ("event_link", self.event_link)]
        matching_events = self.db.get_rows("events", identifier)

        # don't add if the eventDate is more than
        # 180 days (~6 months) from now
        if len(matching_events) == 0 and (self.event_date - self.today).days <= 180:
            self.logger.info(f"Adding {self.title} from {self.event_link}")
            self.db.add_row("events", event_details)
            self.db.close()
        elif len(matching_events) > 0:
            matching_event = matching_events[0]
            for col, new_val in zip(columns, event_details):
                if new_val != matching_event[col] and col not in [
                    "date_added",
                    "in_the_future",
                    "date",
                    "venue",
                ]:
                    self.logger.info(f"Updating {identifier}")
                    self.db.update("events", col, new_val, identifier)
                    self.db.close()

    def check_event_date_year(self):
        """Some venues don't list the year,
        so if the event looks like it's in the past,
        then it's probably next year.

        If thats the case, self.event_date.year is increased by one."""
        if (self.event_date - self.today).days < 0:
            self.event_date = self.event_date.replace(year=self.today.year + 1)

    def log_success(self):
        self.logger.info(f"Scrape completed in {self.timer.elapsed_str}")
        self.scrape_successful = True

    def get_squarespace_calendar(self, collection_id: str) -> Iterable[dict]:
        """Generator that yields a dictionary of event details for venues
        using the squarespace endpoing `{venue_website}/api/open/GetItemsByMonth`.

        `collection_id` should be rendered somewhere in the calendar HTML."""
        date = datetime.now()
        counter = 0
        while True:
            month_year = f"{date:%m-%Y}"
            url = f"{self.venue_info['website'].strip('/')}/api/open/GetItemsByMonth?month={month_year}&collectionId={collection_id}"
            response = get_page(url)
            # Length of 2 means no content
            if len(response.content) == 2 or counter >= 12:
                break
            yield response.json()
            date += timedelta(weeks=4)
            counter += 1

    def scrape(self):
        """Override this."""
        ...
