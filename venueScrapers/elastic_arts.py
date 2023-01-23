from datetime import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            event_links = [
                f'{self.venue_info["website"].strip("/")}{event.get("href")}'
                for event in soup.find_all("a", class_="eventlist-title-link")
            ]
            for event_link in event_links:
                self.reset_event_details()
                soup = get_soup(event_link)
                date = soup.find("time", class_="event-date").get("datetime")
                time = get_text(soup.find("time", class_="event-time-localized-start"))
                if time == "":
                    time = get_text(soup.find("time", class_="event-time-localized"))
                self.event_date = datetime.strptime(
                    f"{date} {time}", "%Y-%m-%d %I:%M %p"
                )
                self.title = get_text(
                    soup.find("h1", attrs={"data-content-field": "title"})
                )
                self.acts = self.title
                info = (
                    soup.find("div", class_="eventitem-column-content")
                    .div.div.find_all("div")[-1]
                    .text
                )
                self.price = info[info.find("$") : info.find(" ", info.find("$"))]
                self.event_link = event_link
                self.info = info
                self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed on {event_link}")


if __name__ == "__main__":
    Scraper().scrape()
