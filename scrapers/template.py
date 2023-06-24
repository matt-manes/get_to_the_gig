import datetime

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

    @GigScraper.chores
    def scrape(self):
        """Scrape calendar."""
        response = self.get_calendar()
        soup = self.as_soup(response)


if __name__ == "__main__":
    Venue().scrape()
