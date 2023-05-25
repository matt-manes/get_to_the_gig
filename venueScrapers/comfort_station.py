from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Iterable

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page


# https://comfortstationlogansquare.org/calendar
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def get_calendar(self, collection_id: str) -> Iterable[dict]:
        date = datetime.now()
        counter = 0
        while True:
            month_year = f"{date:%m-%Y}"
            url = f"https://comfortstationlogansquare.org/api/open/GetItemsByMonth?month={month_year}&collectionId={collection_id}"
            response = get_page(url)
            print(counter)
            if len(response.content) == 2 or counter >= 12:
                break
            yield response.json()
            date += timedelta(weeks=4)
            counter += 1

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            page = get_page(self.venue_info["calendar_url"])
            collection_id = re.findall(r'data-collection-id="[a-zA-Z0-9]+"', page.text)[
                0
            ].split('"')[1]
            for month in self.get_calendar(collection_id):
                for event in month:
                    self.reset_event_details()
                    self.event_date = datetime.fromtimestamp(event["startDate"] / 1000)
                    self.title = event["title"]
                    self.event_link = (
                        f"{self.venue_info['calendar_url'].strip('/')}/{event['urlId']}"
                    )
                    self.price = "Donations Encouraged"
                    self.add_event()
            self.log_success()
        except:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
