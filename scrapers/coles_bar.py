import json
import re
from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://www.colesbarchicago.com
class VenueScraper(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[str]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        # Extract events
        events = []
        for div in soup.find_all("div", class_="rhp-event-thumb"):
            try:
                url = div.find("a").get("href")
                events.append(url)
            except Exception as e:
                pass
        return events

    def parse_event(self, url: str) -> models.Event | None:
        try:
            event = models.Event.new()
            event.url = url
            soup = self.as_soup(self.get_page(url))
            for script in soup.find_all("script"):
                if script.get("type") == "application/ld+json":
                    data = json.loads(script.text)
                    event.date = datetime.strptime(
                        data["startDate"], "%Y-%m-%dT%H:%M:%S-0500"
                    )
                    event.title = data["name"]
                    event.acts = event.title
                    event.price = f"${data['offers']['price']}"
                    event.ticket_url = data["offers"]["url"]
                    return event
            raise Exception("Could not find event markup script tag.")
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
