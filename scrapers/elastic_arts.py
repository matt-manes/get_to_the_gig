from datetime import datetime
from pathier import Pathier
import re

from gig_scraper_engine import GigScraper, get_soup, get_text, get_page

# https://elasticarts.org/events
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            page = get_page(self.venue_info["calendar_url"])
            collection_id = re.findall(
                r'collectionId":"[a-zA-Z0-9]+"', page.text.replace("&quot;", '"')
            )[0].split('"')[2]
            for month in self.get_squarespace_calendar(collection_id):
                for event in month:
                    self.reset_event_details()
                    self.event_date = datetime.fromtimestamp(event["startDate"] / 1000)
                    self.title = event["title"]
                    self.price = "$15+"
                    self.event_link = (
                        f"{self.venue_info['website'].strip('/')}{event['fullUrl']}"
                    )
                    self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed.")


if __name__ == "__main__":
    Scraper().scrape()
