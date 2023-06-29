from datetime import datetime

from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://www.emptybottle.com
class VenueScraper(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[dict]:
        url = "https://app.ticketmaster.com/discovery/v2/events.json?size=200&apikey=GmC9AB6l4pDhA5yhg4dgD3G0AEDK8wmL&venueId=KovZpZAId16A&venueId=rZ7HnEZ178O8A&venueId=rZ7HnEZ17a4Af&venueId=KovZ917AEIJ&venueId=KovZ917AEEX&venueId=KovZpZAFJ1EA&venueId=KovZpZAFEFAA&venueId=KovZpaptBe&venueId=KovZpaptYe&venueId=KovZpZAkt67A&venueId=KovZ917AEIJ"
        response = self.get_page(url)
        data = response.json()
        return data["_embedded"]["events"]

    def parse_event(self, data: dict) -> models.Event | None:
        try:
            event = models.Event.new()
            event.age_restriction = "21+"
            event.title = data["name"]
            event.acts = event.title
            event.url = data["url"]
            start = data["dates"]["start"]
            event.date = datetime.strptime(
                f"{start['localDate']} {start['localTime']}", "%Y-%m-%d %H:%M:%S"
            )
            genre = data["classifications"][0]
            if "genre" in genre and "subGenre" in genre:
                event.genres = f"{genre['genre']['name']}/{genre['subGenre']['name']}"
            elif "genre" in genre:
                event.genres = genre["genre"]["name"]
            else:
                event.genres = genre["segment"]["name"]
            prices = data["priceRanges"][0]
            if prices["min"] == prices["max"]:
                event.price = f"${prices['min']}"
            else:
                event.price = f"${prices['min']}-${prices['max']}"
            return event
        except Exception:
            # input(json.dumps(data))
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
