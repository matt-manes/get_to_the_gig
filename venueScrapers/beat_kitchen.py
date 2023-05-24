import datetime
from pathlib import Path
import re
import json

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page

# https://www.beatkitchen.com/calendar/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            url = self.venue_info["calendar_url"]
            response = get_page(url)
            src = response.text
            # There's a script tag with all the calendar elements in a list of dictionaries format
            events = re.findall(r"events: \[[^\]]+\]", src)[0]
            # Fix all the quotes so json module can load it
            events = (
                events[events.find(":") + 1 :].replace('"', '\\"').replace("'", '"')
            )
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
            for event in events:
                self.reset_event_details()
                self.event_date = datetime.datetime.strptime(
                    event["start"], "%Y-%m-%d %H:%M:%S"
                )
                if datetime.datetime.now() < self.event_date:
                    self.title = event["title"]
                    self.acts = event["title"]
                    url = f"https://www.beatkitchen.com/event-details/{event['id']}"
                    soup = get_soup(url)
                    print(url)
                    self.genres = soup.find("div", class_="tw-genre").text
                    self.info = soup.find("div", class_="tw-age-restriction").text
                    price = soup.find("div", class_="tw-price")
                    self.price = price.text if price else "Free"
                    self.event_link = (
                        soup.find("div", class_="tw-buy-box").find("a").get("href")
                    )
                    self.event_link = self.event_link[: self.event_link.find("?")]
                    self.add_event()
            self.log_success()
        except Exception as e:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
