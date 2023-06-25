from datetime import datetime
import re
from gig_scraper import GigScraper
from pathier import Pathier
import json

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models

# not_ready (This file will be ignored by scrape_venues.py until this comment is removed.)
# calendar url: https://www.beatkitchen.com/calendar
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def parse_events_data(self, source: str) -> list[dict]:
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

    def parse_event(self, listing: dict) -> models.Event:
        """Parse an individual event."""
        event = models.Event.new()
        event.date = datetime.strptime(listing["start"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < event.date:
            event.title = listing["title"]
            event.acts = listing["title"]
            event.url = f"https://www.beatkitchen.com/event-details/{listing['id']}"
            soup = self.as_soup(self.get_page(event.url))
            event.genres = soup.find("div", class_="tw-genre").text
            event.age_restriction = soup.find("div", class_="tw-age-restriction").text
            price_tag = soup.find("div", class_="tw-price")
            event.price = price_tag.text if price_tag else "Free"
            event.ticket_url = (
                soup.find("div", class_="tw-buy-box").find("a").get("href")
            )
            event.ticket_url = event.ticket_url[: event.ticket_url.find("?")]
        else:
            event.in_the_future = False
        return event

    @GigScraper.chores
    def scrape(self):
        """Scrape calendar."""
        try:
            response = self.get_calendar()
            soup = self.as_soup(response)
            try:
                events = self.parse_events_data(response.text)
            except Exception as e:
                raise RuntimeError(
                    "Failed to parse script tag in 'self.parse_events_data()'"
                )
            for listing in events:
                try:
                    event = self.parse_event(listing)
                    if event.in_the_future:
                        self.add_event(event)
                except Exception as e:
                    self.event_fail(event)
        except Exception as e:
            self.logger.exception("Unexpected failure.")


if __name__ == "__main__":
    Venue().scrape()
