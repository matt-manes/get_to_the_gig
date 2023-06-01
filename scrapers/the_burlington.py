from datetime import datetime, timedelta
from pathier import Pathier
import json
from typing import Iterable

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page

# https://www.theburlingtonbar.com/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            collection_id = json.loads(
                soup.find(
                    "div", class_="sqs-block calendar-block sqs-block-calendar"
                ).get("data-block-json")
            )["collectionId"]
            for month in self.get_squarespace_calendar(collection_id):
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
