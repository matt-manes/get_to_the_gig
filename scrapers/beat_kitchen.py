from datetime import datetime
import re
from gig_scraper import GigScraper
from pathier import Pathier
import json

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models

# calendar url: https://www.beatkitchen.com/calendar
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        response = self.get_calendar()
        source = response.text
        # There's a script tag with all the calendar elements in a list of dictionaries format
        events = re.findall(r"events: \[[^\]]+\]", source)[0]
        # Fix all the quotes so json module can load it
        events = events[events.find(":") + 1 :].replace('"', '\\"').replace("'", '"')
        events = [event.strip() for event in events.splitlines()]
        # None of the dict keys are quoted
        for i, event in enumerate(events):
            if not event.startswith(("{", "}", "[", "]")):
                key, value = event.split(":", 1)
                events[i] = f'"{key}":{value}'
        # Last curly brace has a trailing comma
        events[-2] = "}"
        events = "\n".join(events)
        events = json.loads(events)
        return events

    def parse_event(self, data: dict) -> models.Event | None:
        """Parse an individual event. Returns `None` if an exception occurs and dumps details to log."""
        try:
            event = models.Event.new()
            event.date = datetime.strptime(data["start"], "%Y-%m-%d %H:%M:%S")
            event.title = data["title"]
            event.acts = data["title"]
            event.url = f"https://www.beatkitchen.com/event-details/{data['id']}"
            soup = self.as_soup(self.get_page(event.url))
            event.genres = soup.find("div", class_="tw-genre").text
            event.age_restriction = soup.find("div", class_="tw-age-restriction").text
            price_tag = soup.find("div", class_="tw-price")
            event.price = price_tag.text if price_tag else "Free"
            try:
                event.ticket_url = (
                    soup.find("div", class_="tw-buy-box").find("a").get("href")
                )
                event.ticket_url = event.ticket_url[: event.ticket_url.find("?")]
            except Exception as e:
                pass
            return event
        except Exception as e:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
