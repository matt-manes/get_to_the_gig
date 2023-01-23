from datetime import datetime, timedelta
from pathlib import Path

from gig_scraper_engine import GigScraper, get_soup, get_text


# https://comfortstationlogansquare.org/calendar
class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Path(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            #'junk' is just to initialize the while loop
            events_found = ["junk"]
            event_links = []
            i = 0
            while len(events_found) > 0:
                url_date = (self.today + timedelta(weeks=i * 4)).strftime("%m-%Y")
                soup = get_soup(
                    f'{self.venue_info["calendar_url"]}?view=calendar&month={url_date}'
                )
                events_found = [
                    f'{self.venue_info["website"]}{e.a.get("href").strip("/")}'
                    for e in soup.find_all("h1")
                ]
                event_links.extend(events_found)
                i += 1

            for event_link in event_links:
                self.reset_event_details()
                self.event_link = event_link
                soup = get_soup(event_link)
                date = soup.find("time", class_="event-date").get("datetime")
                time = get_text(soup.find("time", class_="event-time-12hr-start"))
                self.event_date = datetime.strptime(
                    f"{date} {time}", "%Y-%m-%d %I:%M %p"
                )
                self.title = get_text(soup.find("h1", class_="eventitem-title"))
                self.acts = get_text(soup.find("h3")).replace("Work by", "").strip()
                if self.acts == "":
                    self.acts = self.title
                self.price = "Donations Encouraged"
                deets = soup.find_all("p", class_="", style="white-space:pre-wrap;")
                self.act_links = "\n".join(
                    e.get("href")
                    for p in deets
                    for e in p.find_all("a")
                    if "spotify" not in e.get("href")
                    and "forms.gle" not in e.get("href")
                )
                self.info = "\n".join(get_text(p) for p in deets)
                self.add_event()
            self.log_success()
        except:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
