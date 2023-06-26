from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://constellation-chicago.com
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[BeautifulSoup]:
        page = 1
        events = []
        while True:
            soup = self.as_soup(self.get_page(f"{self.venue.url}/?sepage={page}"))
            listings = soup.find_all("div", class_="event-info-block")
            if not listings:
                break
            events.extend(listings)
            page += 1
        return events

    def parse_event(self, data: BeautifulSoup) -> models.Event | None:
        try:
            event = models.Event.new()
            event.date = datetime.strptime(
                f"{data.find('p', class_='fs-18 bold mt-1r date').text}-{data.find('span',class_='see-showtime').text}",
                "%a %b %d-%H:%M%p",
            )
            event.date = event.date.replace(year=datetime.now().year)
            if (datetime.now() - event.date).days > 30:
                event.date = event.date.replace(year=datetime.now().year + 1)
            event.title = data.find("a").text
            event.acts = event.title
            event.price = data.find("p", class_="fs-12 ages-price").text
            event.url = data.find("a").get("href")
            event.genres = data.find("p", class_="fs-12 genre").text
            return event
        except Exception:
            self.event_fail(event)
            return None

    @GigScraper.chores
    def scrape(self):
        try:
            try:
                events = self.get_events()
            except Exception:
                self.logger.exception("Error in get_events().")
            else:
                for listing in events:
                    event = self.parse_event(listing)
                    if event:
                        self.add_event(event)
        except Exception as e:
            self.logger.exception("Unexpected failure.")


if __name__ == "__main__":
    Venue().scrape()
