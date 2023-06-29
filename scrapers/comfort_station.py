import re
from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://comfortstationlogansquare.org/calendar
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        response = self.get_calendar()
        collection_id = re.findall(r'data-collection-id="[a-zA-Z0-9]+"', response.text)[
            0
        ].split('"')[1]
        # Extract events
        return self.get_squarespace_events(collection_id)

    def parse_event(self, data: dict) -> models.Event | None:
        try:
            event = models.Event.new()
            event.title = data["title"]
            event.date = datetime.fromtimestamp(int(data["startDate"] / 1000))
            event.url = f"{self.venue.calendar_url}/{data['urlId']}"
            event.price = "Donations Encouraged"
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
