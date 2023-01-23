import time
from datetime import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_text
from seleniumuser import User


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        user = User(headless=True)
        try:
            user.get(self.venue_info["calendar_url"])
            time.sleep(5)
            soup = user.get_soup()
            event_links = [
                f"{self.venueInfo['website']}{ele.get('href').strip('/')}"
                for ele in soup.find_all("a", class_="product-group__link")
            ]
            for event_link in event_links:
                self.reset_event_details()
                user.get(event_link)
                time.sleep(5)
                soup = user.get_soup()
                date = get_text(soup.find("span", class_="event-date-range__start"))
                self.event_date = datetime.strptime(
                    f"{self.today.year} {date}", "%Y %a, %b %d, %I:%M %p"
                )
                self.check_event_date_year()
                self.title = get_text(soup.find("div", class_="product__title"))
                self.acts = self.title[self.title.find("-") + 2 :]
                self.price = get_text(
                    soup.find("div", class_="product__header").find("h3")
                )
                self.event_link = event_link
                self.info = get_text(
                    soup.find("div", class_="w-wrapper product-description")
                )
                self.add_event()

            self.log_success()
        except:
            self.logger.exception(f"Scrape failed on {event_link}")
        user.close_browser()


if __name__ == "__main__":
    Scraper().scrape()
