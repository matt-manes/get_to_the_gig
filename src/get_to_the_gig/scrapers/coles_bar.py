import json
from datetime import datetime
from functools import cached_property

import gruel
import quickpool
from bs4 import BeautifulSoup, Tag
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel


# calendar url: https://www.colesbarchicago.com
class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> BeautifulSoup:  # change `Any` to appropriate type
        return self._item

    @cached_property
    def event_markup(self) -> dict[str, Any]:
        for script in self.item.find_all("script"):
            if script.get("type") == "application/ld+json":
                return json.loads(script.text)
        raise exceptions.MissingSourceError(
            "Cole's Bar: Could not find `application/ld+json` script tag."
        )

    def _parse_date(self) -> None:
        self.event.date = datetime.strptime(
            self.event_markup["startDate"], "%Y-%m-%dT%H:%M:%S-0500"
        )

    def _parse_title_acts(self) -> None:
        self.event.title = self.event_markup["name"]
        self.event.acts = self.event.title

    def _parse_price(self) -> None:
        self.event.price = f"${self.event_markup['offers']['price']}"

    def _parse_urls(self) -> None:
        self.event.url = self.event_markup["url"]
        self.event.ticket_url = self.event_markup["offers"]["url"]

    def _parse_age_restriction(self) -> None:
        age_div = self.item.find("div", class_="col-12 eventAgeRestriction px-0")
        if isinstance(age_div, Tag):
            self.event.age_restriction = age_div.text


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    def get_event_urls(self, source: gruel.Response) -> list[str]:
        """Get the event urls from the homepage."""
        soup = source.get_soup()
        urls: list[str] = []
        for div in soup.find_all("div", class_="rhp-event-thumb"):
            if not isinstance(div, Tag):
                continue
            a = div.find("a")
            if isinstance(a, Tag):
                url = str(a.get("href"))
                if url and url not in urls:
                    urls.append(url)
        return urls

    def get_pages(self, urls: list[str]) -> list[gruel.Response]:
        """Request and return the responses of `urls`."""
        pool = quickpool.ThreadPool(
            [self.request] * len(urls), [(url,) for url in urls], max_workers=3
        )
        return pool.execute(self.test_mode)

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[BeautifulSoup]:
        urls = self.get_event_urls(source)
        return [response.get_soup() for response in self.get_pages(urls)]


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
