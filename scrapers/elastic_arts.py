import re
from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://elasticarts.org/events
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        response = self.get_calendar()
        collection_id = re.findall(
            r'collectionId":"[a-zA-Z0-9]+"', response.text.replace("&quot;", '"')
        )[0].split('"')[2]
        return self.get_squarespace_events(collection_id)

    def parse_event(self, data: dict) -> models.Event | None:
        try:
            event = models.Event.new()
            event.date = datetime.fromtimestamp(int(data["startDate"] / 1000))
            event.title = data["title"]
            event.price = "$15+"
            event.url = f"{self.venue.url}/{data['fullUrl']}"
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
