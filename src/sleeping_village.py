import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page

# https://sleeping-village.com/events/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            events = []
            for i in range(1, 6):
                events.extend(
                    get_page(
                        f"https://sleeping-village.com/api/plot/v1/events?page={i}"
                    ).json()
                )
            for event in events:
                self.reset_event_details()
                self.event_date = datetime.datetime.strptime(
                    event["dateTime"], "<span>%a, %b %d %H:%M%p<span>"
                )
                self.event_date = self.event_date.replace(year=2023)
                self.check_event_date_year()
                self.title = event["title"]
                if "lineup" in event:
                    self.acts = ", ".join(
                        act["title"] for act in event["lineup"]["standard"]
                    )
                else:
                    self.acts = self.title
                self.price = f'${event["tickets"][0]["price"]}'
                if self.price == "$0":
                    self.price = "Free"
                self.event_link = event["permalink"]
                self.info = event["description"]
                self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
