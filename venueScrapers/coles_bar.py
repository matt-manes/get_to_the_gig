import json
import re
from datetime import datetime
from pathlib import Path

from gig_scraper_engine import GigScraper, get_page, get_soup


# https://www.colesbarchicago.com/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def get_event_links(self) -> list[str]:
        soup = get_soup("https://www.colesbarchicago.com/")
        events = []
        for div in soup.find_all("div", class_="image-wrapper"):
            try:
                url = div.find("a").get("href")
                events.append(url)
            except Exception as e:
                pass
        return events

    def get_event_data(self, url: str) -> dict | None:
        soup = get_soup(url)
        data = None
        for script in soup.find_all("script"):
            if "General Data Points" in script.text:
                data = script.text
                break
        if not data:
            return data
        data = re.findall(r"// Track[^;]+", data)[0]
        data = data[data.find("{") : data.rfind("}") + 1].replace("'", '"')
        return json.loads(data)["ecommerce"]["detail"]["products"][0]

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            events = self.get_event_links()
            for event in events:
                self.reset_event_details()
                data = self.get_event_data(event)
                self.event_date = datetime.strptime(
                    data["variant"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                if self.event_date > datetime.now():
                    self.title = data["name"]
                    self.acts = self.title
                    self.price = f"${data['priceDetails'][0]['price']}"
                    self.event_link = event
                    self.add_event()
            self.log_success()
        except:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
