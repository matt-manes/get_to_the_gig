from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# not_ready (This file will be ignored by scrape_venues.py until this comment is removed.)
# calendar url:
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict | BeautifulSoup]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        # Extract events
        events = []
        return events

    def parse_event(self, listing: dict | BeautifulSoup) -> models.Event | None:
        try:
            event = models.Event.new()
            # Populate `event` from `listing`.
            return event
        except Exception:
            self.event_fail(event)
            return None

    @GigScraper.chores
    def scrape(self):
        try:
            try:
                events = self.get_events()
            except Exception:
                self.logger.exception("Error in get_events().")
            else:
                for listing in events:
                    event = self.parse_event(listing)
                    if event:
                        self.add_event(event)
        except Exception as e:
            self.logger.exception("Unexpected failure.")


if __name__ == "__main__":
    Venue().scrape()
