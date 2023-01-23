import json
from datetime import datetime
from pathlib import Path

from get_eventbrite_event_info import get_event_info
from gig_scraper_engine import GigScraper
from seleniumuser import User


# https://cobralounge.com/events/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        user = User(headless=True)
        try:
            user.get(self.venue_info["calendar_url"])
            try:
                user.click("//button[@type='button']")
            except:
                pass
            soup = user.get_soup()
            dice_event_list = soup.find("div", class_="dice-widget").div.div.find_all(
                "script", attrs={"type": "application/ld+json"}
            )
            non_dice_event_list = [
                event for event in soup.find_all("article") if not event.find("script")
            ]
            for event in dice_event_list:
                deets = json.loads(event.text)[0]
                self.reset_event_details()
                try:
                    self.event_date = datetime.strptime(
                        deets["startDate"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                except Exception as e:
                    pass
                try:
                    self.title = deets["name"]
                except:
                    pass
                try:
                    self.acts = "\n".join(p["name"] for p in deets["performers"])
                except:
                    pass
                try:
                    self.price = "$" + str(deets["offers"][0]["price"])
                except:
                    pass
                try:
                    self.event_link = deets["offers"][0]["url"]
                except:
                    pass
                try:
                    self.info = deets["description"]
                except:
                    pass
                self.add_event()
            for event in non_dice_event_list:
                self.reset_event_details()
                self.event_link = event.div.div.div.a.get("href")
                event_info = get_event_info(self.event_link)
                self.event_date = event_info["date"]
                self.title = event_info["name"]
                self.acts = self.title
                self.price = event_info["price"]
                self.info = event_info["description"]
                self.add_event()
            self.log_success()
        except:
            self.logger.exception("Scrape failed")
        user.close_browser()


if __name__ == "__main__":
    Scraper().scrape()
