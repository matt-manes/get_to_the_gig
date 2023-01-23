import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            base_url = self.venue_info["website"]
            url = self.venue_info["calendar_url"]
            soup = get_soup(url)
            events = soup.find("div", attrs={"id": "productList"}).find_all("a")
            for event in events:
                self.reset_event_details()
                self.event_link = f'{base_url.strip("/")}{event.get("href")}'
                soup = get_soup(self.event_link)
                self.title = soup.find("title").text.replace("— Cole's Bar", "")
                date_string = self.title[: self.title.find(":")].lower()
                if "cole's holiday market" in date_string or "new years" in date_string:
                    continue
                try:
                    self.event_date = datetime.datetime.strptime(
                        f"{self.today.year} {date_string} 10:00 pm",
                        "%Y %A %B %d %I:%M %p",
                    )
                except:
                    try:
                        self.event_date = datetime.datetime.strptime(
                            f"{self.today.year} {date_string} 10:00 pm",
                            "%Y %A %B %dth %I:%M %p",
                        )
                    except Exception as e:
                        try:
                            self.event_date = datetime.datetime.strptime(
                                f"{self.today.year} {date_string} 10:00 pm",
                                "%Y %A %B %dst %I:%M %p",
                            )
                        except Exception as e:
                            self.event_date = datetime.datetime.strptime(
                                f"{self.today.year} {date_string} 10:00 pm",
                                "%Y %A %B %dnd %I:%M %p",
                            )
                self.check_event_date_year()
                self.acts = self.title[self.title.find(":") + 2 :]
                self.price = soup.find(
                    "meta", attrs={"property": "product:price:amount"}
                ).get("content")
                product_excerpt = soup.find("div", class_="product-excerpt")
                if product_excerpt:
                    self.info = "\n".join(ele.text for ele in product_excerpt.children)
                    self.act_links = "\n".join(
                        ele.get("href")
                        for ele in product_excerpt.find_all("a")
                        if "spotify" not in ele.get("href")
                    )
                self.add_event()
            self.log_success()
        except:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
