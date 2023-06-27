from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://goldendagger.com
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[BeautifulSoup]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        pages = int(
            soup.find("span", class_="tw-paginate-text")
            .findChildren("span", class_="link")[-1]
            .a.text
        )
        events = []
        for page in range(pages):
            if page > 0:
                soup = self.get_soup(f"{self.venue.calendar_url}?twpage={page}")
            events.extend(soup.find_all("div", class_="tw-name"))
        return events

    def parse_event(self, data: BeautifulSoup) -> models.Event | None:
        try:
            event = models.Event.new()
            event.url = data.a.get("href")
            soup = self.get_soup(event.url)
            day = self.clean(soup.find("span", class_="tw-day-of-week").text)
            date = self.clean(soup.find("span", class_="tw-event-date").text)
            time = self.clean(soup.find("span", class_="tw-event-time").text)
            event.date = datetime.strptime(
                f"{day} {date} {time}", "%a %B %d, %Y %I:%M %p"
            )
            event.title = self.clean(soup.find("div", class_="tw-name").text)
            event.acts = ", ".join(
                act.text
                for act in soup.find("div", class_="tw-opening-act").findChildren(
                    "span"
                )
            )
            event.price = self.clean(soup.find("div", class_="tw-price").text)
            event.act_urls = "\n".join(
                subsection.find("div", class_="tw-description").text
                for subsection in soup.find_all("div", class_="tw-subsection")
                if subsection.find("div", class_="tw-description") is not None
            )
            event.genres = self.clean(soup.find("div", class_="tw-genre").text)
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
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
