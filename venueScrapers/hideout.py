from datetime import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text

# not_ready
# https://hideoutchicago.com/events/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            event_links = [
                event.get("href")
                for event in soup.find_all(
                    "a", class_="url", attrs={"id": "eventTitle"}
                )
            ]
            for event_link in event_links:
                self.reset_event_details()
                soup = get_soup(event_link)
                date = get_text(soup.find("span", class_="eventStDate text-uppercase"))
                time = (
                    get_text(
                        soup.find("span", class_="font0Med75"), clean=False
                    ).lstrip()
                    + " "
                )
                time = time[time.find(" ") + 1 : time.find(" ", time.find(" ") + 1)]
                self.event_date = datetime.strptime(
                    f"{date} {time}",
                    "%A, %B %d, %Y %I%p"
                    if ":" not in time
                    else "%A, %B %d, %Y %I:%M%p",
                )
                self.title = get_text(soup.find("span", attrs={"id": "eventTitle"}))
                self.acts = self.title
                self.price = get_text(
                    soup.find("div", class_="d-block eventsColor eventCost")
                )
                if self.price == "":
                    self.price = "Free or Sold Out"
                self.event_link = event_link
                self.act_links = "\n".join(
                    ele.get("href")
                    for ele in soup.find(
                        "div", class_="col-sm-12 px-0 singleEventDescription emptyDesc"
                    ).find_all("a")
                    if "spotify" not in ele.get("href")
                )
                self.info = get_text(
                    soup.find(
                        "div", class_="col-sm-12 px-0 singleEventDescription emptyDesc"
                    )
                )
                self.add_event()

            self.log_success()
        except:
            self.logger.exception(f"Scrape failed on {event_link}")


if __name__ == "__main__":
    Scraper().scrape()
