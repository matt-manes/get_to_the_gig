import datetime

from gig_scraper_engine import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models

# not_ready
# calendar url:
class Venue(GigScraper):
    def scrape(self):
        """Scrape calendar."""
        self.logger.info("Scrape started.")
        response = self.get_calendar()
        soup = self.as_soup(response)


if __name__ == "__main__":
    Venue().scrape()
