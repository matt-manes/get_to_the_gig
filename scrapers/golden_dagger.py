from datetime import datetime
from pathier import Pathier

from gig_scraper_engine import GigScraper, get_soup, get_text


class Scraper(GigScraper):
    def __init__(self):
        super().__init__(Pathier(__file__))

    def scrape(self):
        self.logger.info("Scrape started")
        try:
            soup = get_soup(self.venue_info["calendar_url"])
            pages = int(
                soup.find("span", class_="tw-paginate-text")
                .findChildren("span", class_="link")[-1]
                .a.text
            )
            for page in range(pages):
                if page > 0:
                    soup = get_soup(f'{self.venue_info["calendar_url"]}?twpage={page}')
                events = soup.find_all("div", class_="tw-name")
                for event in events:
                    self.reset_event_details()
                    event_link = event.a.get("href")
                    soup = get_soup(event_link)
                    day = get_text(soup.find("span", class_="tw-day-of-week"))
                    date = get_text(soup.find("span", class_="tw-event-date"))
                    time = get_text(soup.find("span", class_="tw-event-time"))
                    self.event_date = datetime.strptime(
                        f"{day} {date} {time}", "%a %B %d, %Y %I:%M %p"
                    )
                    self.title = get_text(soup.find("div", class_="tw-name"))
                    self.acts = "\n".join(
                        act.text
                        for act in soup.find(
                            "div", class_="tw-opening-act"
                        ).findChildren("span")
                    )
                    self.price = get_text(soup.find("div", class_="tw-price"))
                    self.event_link = event_link
                    self.act_links = "\n".join(
                        ele.get("href")
                        for ele in soup.find_all("a", class_="officialwebsite")
                    )
                    self.info = "\n".join(
                        subsection.find("div", class_="tw-description").text
                        for subsection in soup.find_all("div", class_="tw-subsection")
                        if subsection.find("div", class_="tw-description") is not None
                    )
                    self.genres = get_text(soup.find("div", class_="tw-genre"))
                    self.add_event()
            self.log_success()
        except:
            self.logger.exception("Scrape failed")


if __name__ == "__main__":
    Scraper().scrape()
