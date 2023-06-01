import datetime
from pathier import Pathier
from gig_scraper_engine import GigScraper, get_soup

# not_ready
# $calendar_url
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def scrape(self):
        """Scrape calendar."""
        self.logger.info("Scrape started")
        venue_url = self.venue_info["website"]
        calendar_url = self.venue_info["calendar_url"]


if __name__ == "__main__":
    Scraper().scrape()
