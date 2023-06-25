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

    def parse_event(self, listing: dict | BeautifulSoup) -> models.Event:
        event = models.Event.new()
        """ Parsing code """
        return event

    @GigScraper.chores
    def scrape(self):
        """Scrape calendar."""
        try:
            response = self.get_calendar()
            soup = self.as_soup(response)
            events: dict | BeautifulSoup
            for listing in events:
                try:
                    event = self.parse_event(listing)
                    # self.parse_event should determine whether `event` is in the future or not
                    if event.in_the_future:
                        self.add_event(event)
                except Exception as e:
                    self.event_fail(event)
        except Exception as e:
            self.logger.exception("Unexpected failure.")


if __name__ == "__main__":
    Venue().scrape()
