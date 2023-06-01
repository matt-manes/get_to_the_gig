import json
from datetime import datetime, timedelta
from pathier import Pathier
import re
import requests
from whosyouragent import get_agent

from gig_scraper_engine import GigScraper, get_page


# https://cobralounge.com/events/
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def get_events(self) -> dict:
        page = get_page(self.venue_info["calendar_url"]).text
        api_key = re.findall(r'"apiKey":"[a-zA-Z0-9]+"', page)[0]
        api_key = api_key.split(":")[1].strip('"')
        response = requests.get(
            "https://events-api.dice.fm/v1/events?page[size]=100&types=linkout,event&filter[venues][]=Cobra%20Lounge",
            headers={"user-agent": get_agent(), "x-api-key": api_key},
        )
        return response.json()["data"]

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            events = self.get_events()
            for event in events:
                if not event["raw_description"]:
                    continue
                self.reset_event_details()
                # The dates listed in a timezone that's +5 hours
                self.event_date = datetime.strptime(
                    event["date"], "%Y-%m-%dT%H:%M:%SZ"
                ) - timedelta(hours=5)
                self.title = event["name"]
                self.acts = ", ".join(event["artists"])
                if event["ticket_types"]:
                    self.price = (
                        f"${event['ticket_types'][0]['price']['total']/100:.2f}"
                    )
                else:
                    try:
                        self.price = f"${event['price']/100:.2f}"
                    except Exception as e:
                        self.price = "n/a"
                self.event_link = event["url"]
                self.info = event["age_limit"]
                self.genres = ", ".join(
                    tag.split(":")[1] for tag in event["genre_tags"]
                )
                self.add_event()
            self.log_success()
        except:
            self.logger.exception(f"Scrape failed\n{json.dumps(event)}")


if __name__ == "__main__":
    Scraper().scrape()
