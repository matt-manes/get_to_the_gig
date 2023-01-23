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
            event_list = [
                soup.find("div", attrs={"id": "seetickets"}).findChild("article"),
                *soup.find("div", attrs={"id": "seetickets"})
                .findChild("article")
                .find_next_siblings("article"),
            ]
            for event in event_list:
                self.reset_event_details()
                event_link = event.find("a").get("href")
                date = get_text(
                    event.find("div", class_="detail detail_event_date").find(
                        "div", class_="name"
                    )
                )
                time = get_text(
                    event.find("div", class_="detail detail_event_time").find(
                        "div", class_="name"
                    )
                )
                self.event_date = datetime.strptime(
                    f"{self.today.year} {date} {time}", "%Y %a %b %d %I:%M %p"
                )
                self.check_event_date_year()
                self.title = get_text(event.find("h1", class_="event-name headliners"))
                self.acts = self.title
                try:
                    self.price = get_text(
                        event.find("div", class_="detail detail_price_range").find(
                            "div", class_="name"
                        )
                    )
                except:
                    pass
                self.event_link = event_link
                self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
