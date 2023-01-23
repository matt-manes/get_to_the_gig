from datetime import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text


# https://www.theburlingtonbar.com/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            for i in range(3):
                if i == 0:
                    soup = get_soup(self.venue_info["calendar_url"])
                else:
                    next_month = (
                        soup.find("div", class_="nextmonth").a.get("href").strip("/")
                    )
                    soup = get_soup(f'{self.venue_info["calendar_url"]}{next_month}')
                events = soup.find_all("td", class_="cal_dayshasevents")
                for event in events:
                    self.reset_event_details()
                    date_link = event.a.get("href")[1:]
                    date_link = date_link[
                        date_link.find("/") + 1 : date_link.rfind("/")
                    ]
                    self.event_date = datetime.strptime(
                        f"{date_link} 8pm", "%Y/%m/%d %I%p"
                    )
                    self.title = get_text(event.find("a", class_="cal_titlelink"))
                    self.acts = self.title
                    self.price = "$10"
                    event_link = (
                        event.find("a", class_="cal_titlelink").get("href").strip("/")
                    )
                    self.event_link = f'{self.venue_info["website"]}{event_link}'
                    self.add_event()
            self.log_success()
        except Exception as e:
            self.logger.exception(e)


if __name__ == "__main__":
    Scraper().scrape()
