import json
import re
from datetime import datetime

from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://lh-st.com
class Venue(GigScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem

    def get_events(self) -> list[str]:
        response = self.get_calendar()
        soup = self.as_soup(response)
        # Extract events
        events = [
            div.find("a").get("href")
            for div in soup.find_all(
                "div", class_="card-footer text-start align-items-center"
            )
            if self.venue.name.split()[0] in div.find("span").text
        ]
        return events

    def parse_event(self, url: str) -> models.Event | None:
        try:
            event = models.Event.new()
            event.url = url
            soup = self.get_soup(url)
            main = soup.find("div", class_="mainContent")
            event.title = f"{main.find('div').text} {main.find_all('div')[1].find('h2').text[:-1]}"
            script = soup.find("body").find("script").text
            id_ = re.findall(r"eventID: '([0-9]+)'", script)[0]
            date = re.findall(r"dateandTime: '([0-9 a-zA-Z/:]+)'", script)[0]
            event.date = datetime.strptime(date, "%m/%d/%Y %I:%M %p")
            try:
                headliner = (
                    soup.find("div", class_="tessera-artists").find("h2").find("a")
                )
                acts = [(headliner.text, headliner.get("href"))]
            except Exception as e:
                headliner = soup.find("div", class_="tessera-artists").find("h2")
                acts = [(headliner.text, "")]
            if supports := soup.find("div", class_="additional_artists"):
                try:
                    acts.extend(
                        [
                            (support.text, support.get("href"))
                            for support in supports.find_all("a")
                        ]
                    )
                except Exception as e:
                    acts.extend(
                        [(support.text, "") for support in supports.find_all("span")]
                    )
            event.acts = ", ".join(act[0] for act in acts)
            event.act_urls = ", ".join(act[1] for act in acts if act[1] != "")
            event.age_restriction = soup.find("div", class_="ages").text

            for a in soup.find("body").find_all("a"):
                if a.text == "GET TICKETS":
                    event.price = "?"
                    event.ticket_url = a.get("href")
                    break
            if not event.price == "?":
                session_id = "RUFBQUFCZ09pMGsxM1cwTjkzMXFTM0ZXN2lTT2RDMG5ISWd0SmxyTTRLZmpGcFZmQS8xNmZocXpIdVU1U015NGJwWlQ1T0E4ZXJGK0RWT2cyNHAybGxtT0x0UT0="
                url = f"https://tickets.lh-st.com/api/v1/products/{id_}"
                response = self.get_page(url, {"SessionId": session_id})
                if response.status_code == 204:
                    event.price = "Free"
                else:
                    data = response.json()
                    event.price = "/".join(
                        f"${ticket['price']}" for ticket in data["campaigns"]
                    )
            return event
        except Exception:
            self.event_fail(event)
            return None


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
