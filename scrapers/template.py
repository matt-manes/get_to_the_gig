from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url:
class VenueScraper(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict | BeautifulSoup | str]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        # Extract events
        events = []
        return events

    def parse_event(self, data: dict | BeautifulSoup | str) -> models.Event | None:
        try:
            event = models.Event.new()
            # Populate `event` from `data`.
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
