import json
from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://www.theburlingtonbar.com
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        collection_id = json.loads(
            soup.find("div", class_="sqs-block calendar-block sqs-block-calendar").get(
                "data-block-json"
            )
        )["collectionId"]
        return self.get_squarespace_events(collection_id)

    def parse_event(self, data: dict) -> models.Event | None:
        try:
            event = models.Event.new()
            event.date = datetime.fromtimestamp(int(data["startDate"] / 1000))
            event.title = data["title"]
            event.acts = event.title
            event.price = "$10"
            event.url = f"{self.venue.calendar_url}/{data['fullUrl']}"
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
