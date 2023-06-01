import datetime
from pathier import Pathier

from gig_scraper_engine import GigScraper, get_text
from seleniumuser import User


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        user = User(headless=True)
        try:
            url = self.venue_info["calendar_url"]
            user.get(url)
            soup = user.get_soup()
            feed = soup.find("div", attrs={"id": "widget-full-feed"})
            events = feed.find_all("div", class_="eb-item")
            for event in events:
                self.reset_event_details()
                date_string = event.find("div", class_="date").text
                time_string = event.find("div", class_="start-time").text
                self.event_date = datetime.datetime.strptime(
                    f"{self.today.year} {date_string} {time_string}",
                    "%Y %a %B %d %I:%M%p",
                )
                self.check_event_date_year()
                self.title = event.find("div", class_="title").text
                self.acts = "\n".join(
                    ele.text
                    for ele in event.find("ul", class_="performing").find_all("li")
                )
                self.event_link = (
                    event.find("a", class_="buy-button")
                    .get("href")
                    .replace("#tickets", "")
                )
                # TicketWeb has started blocking vpns, so this is prone to fail.
                try:
                    user.get(self.event_link)
                    soup = user.get_soup()
                    self.price = get_text(
                        soup.find("div", class_="conversion-bar__panel-info")
                    )
                    self.info = get_text(
                        soup.find("div", class_="has-user-generated-content")
                    )
                except Exception as e:
                    pass
                self.add_event()
            self.log_success()
        except Exception as e:
            self.logger.exception("Scrape Failed")
        user.close_browser()


if __name__ == "__main__":
    Scraper().scrape()
