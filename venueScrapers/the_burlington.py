from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Iterable

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page

# https://www.theburlingtonbar.com/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def get_calendar(self, collection_id: str) -> Iterable[dict]:
        date = datetime.now()
        counter = 0
        while True:
            month_year = f"{date:%m-%Y}"
            url = f"https://www.theburlingtonbar.com/api/open/GetItemsByMonth?month={month_year}&collectionId={collection_id}"
            response = get_page(url)
            if len(response.content) == 2 or counter >= 12:
                break
            yield response.json()
            date += timedelta(weeks=4)
            counter += 1

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            collection_id = json.loads(
                soup.find(
                    "div", class_="sqs-block calendar-block sqs-block-calendar"
                ).get("data-block-json")
            )["collectionId"]
            for month in self.get_calendar(collection_id):
                for event in month:
                    self.reset_event_details()
                    self.event_date = datetime.fromtimestamp(event["startDate"] / 1000)
                    self.title = event["title"]
                    self.acts = self.title
                    self.price = "$10"
                    self.event_link = f"{self.venue_info['calendar_url'].strip('/')}{event['fullUrl']}"
                    self.add_event()
            self.log_success()
        except Exception as e:
            print(e)
            self.logger.exception(e)


if __name__ == "__main__":
    Scraper().scrape()
