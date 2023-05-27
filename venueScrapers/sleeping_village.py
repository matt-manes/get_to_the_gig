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
                # The API has started only returning weekday and time
                # For now, have to make an extra request to the ticket page to get month and numerical day
                # Way slower, but will have to do for now
                soup = get_soup(event["ticket"]["link"])
                date = soup.find(
                    "div", class_="EventDetailsTitle__Date-v4l5yy-2 bdHHkj"
                ).text
                date = date.replace("Sept,", "Sep,")
                try:
                    self.event_date = datetime.datetime.strptime(
                        date, "%a, %d %b, %H:%M %p"
                    )
                except Exception as e:
                    self.event_date = datetime.datetime.strptime(
                        date, "%a, %b %d, %H:%M %p"
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
