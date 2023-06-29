from datetime import datetime
import re
import yaml
from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier
from string import punctuation

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models

yaml.load
# calendar url: https://www.subt.net/calendar
class VenueScraper(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_event_urls(self, src: str) -> dict:
        """Find all event urls and return a dictionary with the id/last path part as keys."""
        urls = re.findall(r"\"(https://www.subt.net/event/tw-eventinfo/(?:.*?))\"", src)
        urls = list(set(urls))
        return {url[url.rfind("/") + 1 :]: url for url in urls}

    def get_events(self) -> list[dict]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        # What a nightmare extracting and loading this turned out to be
        src = response.text.replace("\n", "")
        self.event_urls = self.get_event_urls(src)
        src = " ".join(src.split())
        src = re.findall(r", events: (.*?), eventColor:", src)[0]
        src = re.sub(r"imageUrl:'(.*?) />',", "", src)
        holder = "^*^_-"
        src = src.replace(r"\'", holder).replace("'", '"').replace(holder, "'")
        return yaml.safe_load(src)

    def parse_event(self, data: dict) -> models.Event | None:
        try:
            event = models.Event.new()
            event.title = data["title"]
            event.date = datetime.strptime(data["start"], "%Y-%m-%d %H:%M:%S")
            # past events are still on the calendar, but the event page is blank
            if datetime.now() < event.date:
                event.url = self.event_urls[data["id"]]
                soup = self.get_soup(event.url)
                event.age_restriction = soup.find(
                    "div", class_="eventartists__event__notes"
                ).text
                tickets = soup.find("div", class_="eventartists__event__ticketbutton")
                event.ticket_url = tickets.find("a").get("href")
                event.price = tickets.find("span").text
                event.acts = ", ".join(
                    h2.text.strip()
                    for h2 in soup.find_all("h2", class_="eventartists_artist_name")
                )
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
