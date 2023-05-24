import json
from datetime import datetime
from pathlib import Path
from typing import Iterable
from bs4 import Tag

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def get_event_list(self) -> Iterable[list[Tag]]:
        page = 1
        while True:
            soup = get_soup(f"{self.venue_info['calendar_url']}?sepage={page}")
            events = soup.find_all(
                "div",
                class_="event-info-block",
            )
            if not events:
                break
            yield events
            page += 1

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            events = [
                event for event_list in self.get_event_list() for event in event_list
            ]

            for event in events:
                self.reset_event_details()
                self.event_date = datetime.strptime(
                    f"{event.find('p', class_='fs-18 bold mt-1r date').text}-{event.find('span',class_='see-showtime').text}",
                    "%a %b %d-%H:%M%p",
                )
                self.event_date = self.event_date.replace(year=datetime.now().year)
                if (datetime.now() - self.event_date).days > 30:
                    self.event_date.replace(year=datetime.now().year + 1)
                self.title = event.find("a").text
                self.acts = self.title
                self.price = event.find("p", class_="fs-12 ages-price").text
                self.event_link = event.find("a").get("href")
                self.genres = event.find("p", class_="fs-12 genre").text
                self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
