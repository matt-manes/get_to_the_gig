import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            events = soup.find_all(
                "div", class_="col-12 mt-2 text-center eventMoreInfo"
            )
            for event in events:
                self.reset_event_details()
                event_link = event.a.get("href")
                soup = get_soup(event_link)
                date_string = get_text(
                    soup.find("span", class_="eventStDate text-uppercase")
                )
                time_string = get_text(soup.find("span", class_="font0Med75"))
                time_string = time_string[time_string.rfind(" ") + 1 :]
                self.event_date = datetime.datetime.strptime(
                    f"{self.today.year} {date_string} {time_string}",
                    "%Y %A, %B %d %I%p"
                    if ":" not in time_string
                    else "%Y %A, %B %d %I:%M%p",
                )
                self.check_event_date_year()
                self.title = soup.find("span", attrs={"id": "eventTitle"}).get("title")
                self.acts = self.title
                try:
                    self.price = get_text(
                        soup.find("div", class_="d-block eventsColor eventCost").span
                    )
                except:
                    pass
                self.event_link = event_link
                try:
                    act_links = [
                        ele.get("href")[: ele.get("href").find("?")]
                        for ele in soup.find_all("a", class_="artlink")
                    ]
                    self.act_links = "\n".join(act_links)
                except:
                    pass
                self.info = soup.find(
                    "div", class_="col-sm-12 px-0 singleEventDescription emptyDesc"
                ).text
                try:
                    venue = soup.find("a", class_="noVenueLink").text
                    if venue != "Sleeping Village":
                        self.info = "*Not actually at sleeping village\n" + self.info
                except:
                    pass
                self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed on {event_link}")


if __name__ == "__main__":
    Scraper().scrape()
