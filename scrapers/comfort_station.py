from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Iterable

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page


# https://comfortstationlogansquare.org/calendar
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            page = get_page(self.venue_info["calendar_url"])
            collection_id = re.findall(r'data-collection-id="[a-zA-Z0-9]+"', page.text)[
                0
            ].split('"')[1]
            for month in self.get_squarespace_calendar(collection_id):
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
