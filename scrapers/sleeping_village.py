from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://sleeping-village.com/events
class VenueScraper(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        events = []
        for i in range(1, 6):
            events.extend(
                self.get_page(
                    f"https://sleeping-village.com/api/plot/v1/listings?page={i}"
                ).json()
            )
        # input(events)
        return events

    def parse_event(self, data: dict) -> models.Event | None:
        try:
            event = models.Event.new()
            event.title = data["title"]
            event.date = datetime.strptime(
                data["dateTime"], "<span>%a, %b %d %H:%M%p<span>"
            )
            event.date = event.date.replace(year=2023)
            event = self.check_event_year(event)
            if "lineup" in data:
                event.acts = ", ".join(
                    act["title"] for act in data["lineup"]["standard"]
                )
            else:
                event.acts = event.title
            event.price = f"${data['tickets'][0]['price']}"
            if event.price == "$0":
                event.price = "Free"
            event.url = data["permalink"]
            event.info = data["description"]
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
