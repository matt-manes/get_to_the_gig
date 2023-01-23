import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            url = self.venue_info["calendar_url"]
            soup = get_soup(url)

            num_pages = int(
                soup.find("span", class_="tw-paginate-text")
                .find_all("span", class_="link")[-1]
                .text
            )
            for page in range(num_pages):
                if page != 0:
                    soup = get_soup(f"{url}?twpage={page}")
                events = soup.find_all("div", class_="six columns")
                for event in events:
                    self.reset_event_details()
                    self.title = event.div.a.get("href")
                    self.event_link = event.div.a.get("href")
                    date_string = event.find("span", class_="tw-event-date").text
                    time_string = event.find("span", class_="tw-event-time").text
                    self.event_date = datetime.datetime.strptime(
                        f"{date_string} {time_string}", "%B %d, %Y %I:%M %p"
                    )
                    self.price = get_text(event.find("span", class_="tw-price"))
                    soup = get_soup(self.event_link)
                    self.acts = "\n".join(
                        ele.text
                        for ele in soup.find("div", class_="tw-opening-act").find_all(
                            "span"
                        )
                    )
                    self.genres = soup.find("div", class_="tw-genre").text.strip()
                    self.info = get_text(soup.find("div", class_="tw-description"))
                    self.info = (
                        get_text(soup.find("div", class_="tw-age-restriction"))
                        + "\n"
                        + self.info
                    )
                    self.add_event()
            self.log_success()
        except Exception as e:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
