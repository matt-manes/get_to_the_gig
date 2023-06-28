from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://cdn5.editmysite.com/app/store/api/v28/editor/users/131312941/sites/715381155365579768/products?per_page=60&categories[]=11eb8686dd0a0704b0c60cc47a2b63cc
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict | BeautifulSoup]:
        response = self.get_calendar()
        return response.json()["data"]

    def parse_event(self, data: dict | BeautifulSoup) -> models.Event | None:
        try:
            event = models.Event.new()
            details = data["product_type_details"]
            event.date = datetime.strptime(
                f"{details['start_date']} {details['start_time']}", "%Y-%m-%d %H:%M %p"
            )
            event.title = data["name"]
            high = data["price"]["high_formatted"]
            low = data["price"]["low_formatted"]
            if high == low:
                event.price = high
            else:
                event.price = f"{low}-{high}"
            event.url = f"{self.venue.url}/{data['site_link']}"
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
