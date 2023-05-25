from datetime import datetime
from pathlib import Path
from time import sleep

from gig_scraper_engine import GigScraper, get_soup, get_text
from seleniumuser import User


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        user = User(headless=True)
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            event_links = [
                event.div.div.a.get("href")
                for event in soup.find_all("div", attrs={"data-venue": "Lincoln Hall"})
            ]
            for event_link in event_links:
                self.reset_event_details()
                user.get(event_link)
                try:
                    user.wait_until(
                        lambda: user.find('//*[@class="table tessera-show-tickets"]')
                    )
                except Exception as e:
                    pass
                sleep(1)
                soup = user.get_soup()
                date = get_text(soup.find("strong", class_="month"))
                time = get_text(soup.find("div", class_="time-item text-doors").span)
                time = time.split(" | ")[1]
                time = time[: time.find(" ")]
                self.event_date = datetime.strptime(
                    f"{self.today.year} {date} {time}",
                    "%Y %B %d %I%p" if ":" not in time else "%Y %B %d %I:%M%p",
                )
                self.check_event_date_year()
                self.title = get_text(
                    soup.find("div", class_="tessera-artists").h2
                ).strip(",")
                acts = [self.title]
                try:
                    supporting_acts = [
                        get_text(ele).strip(",")
                        for ele in soup.find(
                            "div", class_="additional-artists"
                        ).find_children("span")
                        if get_text(ele) != ","
                    ]
                except:
                    supporting_acts = []
                self.acts = "\n".join(acts + supporting_acts)
                try:
                    self.price = get_text(
                        soup.find(
                            "table", class_="table tessera-show-tickets"
                        ).tbody.tr.find_all("td")[1]
                    )
                except:
                    self.price = "Free probably"
                self.event_link = event_link
                try:
                    act_links = [
                        soup.find("div", class_="tessera-artists").h2.a.get("href")
                    ]
                except:
                    act_links = []
                try:
                    act_links.extend(
                        [
                            ele.a.get("href")
                            for ele in soup.find(
                                "div", class_="additional-artists"
                            ).find_children("span")
                            if ele.a is not None
                        ]
                    )
                except:
                    pass
                self.act_links = "\n".join(
                    link for link in act_links if "spotify" not in link
                )
                self.info = get_text(soup.find("div", class_="ages").span) + "\n"
                self.info += get_text(soup.find("div", class_="show-description"))
                self.add_event()

            self.log_success()
        except:
            self.logger.exception(f"Scrape failed {event_link}")
        user.close_browser()


if __name__ == "__main__":
    Scraper().scrape()
