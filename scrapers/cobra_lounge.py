import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://cobralounge.com/events
class VenueScraper(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        response = self.get_calendar()
        src = response.text
        api_key = re.findall(r'"apiKey":"[a-zA-Z0-9]+"', src)[0]
        api_key = api_key.split(":")[1].strip('"')
        response = self.get_page(
            "https://events-api.dice.fm/v1/events?page[size]=100&types=linkout,event&filter[venues][]=Cobra%20Lounge",
            {"x-api-key": api_key},
        )
        return [event for event in response.json()["data"] if event["raw_description"]]

    def parse_event(self, data: dict | BeautifulSoup) -> models.Event:
        try:
            event = models.Event.new()
            # The dates listed are timezone that's +5 hours
            event.date = datetime.strptime(
                data["date"], "%Y-%m-%dT%H:%M:%SZ"
            ) - timedelta(hours=5)
            event.title = data["name"]
            event.acts = ", ".join(data["artists"])
            if data["ticket_types"]:
                event.price = f"${data['ticket_types'][0]['price']['total']/100:.2f}"
            else:
                try:
                    event.price = f"${data['price']/100:.2f}"
                except Exception as e:
                    event.price = "n/a"
            event.url = data["url"]
            event.age_restriction = data["age_limit"]
            event.genres = ", ".join(tag.split(":")[1] for tag in data["genre_tags"])
            return event
        except:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
