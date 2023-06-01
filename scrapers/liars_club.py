import time
from datetime import datetime
from pathier import Pathier
import json

from gig_scraper_engine import GigScraper, get_text, get_page


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            data = get_page(
                "https://cdn5.editmysite.com/app/store/api/v28/editor/users/131312941/sites/715381155365579768/products?per_page=60&categories[]=11eb8686dd0a0704b0c60cc47a2b63cc"
            ).json()["data"]
            for event in data:
                self.reset_event_details()
                details = event["product_type_details"]
                self.event_date = datetime.strptime(
                    f"{details['start_date']} {details['start_time']}",
                    "%Y-%m-%d %H:%M %p",
                )
                self.title = event["name"]
                high = event["price"]["high_formatted"]
                low = event["price"]["low_formatted"]
                if high == low:
                    self.price = high
                else:
                    self.price = f"{low}-{high}"
                self.event_link = f"{self.venue_info['website']}{event['site_link']}"
                self.add_event()

            self.log_success()
        except:
            self.logger.exception(f"Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
