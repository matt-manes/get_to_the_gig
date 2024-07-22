from datetime import datetime

import gruel
from bs4 import BeautifulSoup, Tag
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel


# calendar url: https://constellation-chicago.com
class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> Tag:  # change `Any` to appropriate type
        return self._item

    # Add `_parse_` functions below
    def _parse_title_urls(self) -> None:
        title_p = self.item.find("p", class_="fs-18 bold mb-12 title")
        if not isinstance(title_p, Tag):
            return
        self.event.title = title_p.text
        self.event.acts = self.event.title
        a = title_p.find("a")
        if isinstance(a, Tag):
            self.event.url = str(a.get("href"))
            self.event.ticket_url = self.event.url

    def _parse_date(self) -> None:
        time_span = self.item.find("span", class_="see-showtime")
        if not isinstance(time_span, Tag):
            raise RuntimeError(f"Could not find start time for Constellation.")
        time = time_span.text
        date_p = self.item.find("p", class_="fs-18 bold mt-1r date")
        if not isinstance(date_p, Tag):
            raise RuntimeError("Could not find start date for Constellation.")
        date = date_p.text
        # 'Sat Jul 27 8:30PM'
        self.event.date = datetime.strptime(f"{date} {time}", "%a %b %d %I:%M%p")
        self.event.date = self.event.date.replace(year=datetime.now().year)
        self.event.validate_year()

    def _parse_price(self) -> None:
        price_span = self.item.find("span", class_="price")
        if isinstance(price_span, Tag):
            self.event.price = price_span.text


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    def _max_pages(self, soup: BeautifulSoup) -> int:
        pagination = soup.find("ul", class_="seetickets-list-view-pagination")
        if not isinstance(pagination, Tag):
            raise RuntimeError("Could not find pagination for Constellation.")
        return int(pagination.find_all("li")[-1].get("data-see-ajax-page"))

    @override
    def get_source(self) -> list[gruel.Response]:
        page = 1
        responses: list[gruel.Response] = []
        max_pages: int | None = None
        while True:
            response = self.request(f"{self.venue.url}/?sepage={page}")
            responses.append(response)
            if not max_pages:
                max_pages = self._max_pages(response.get_soup())
            if page >= max_pages:
                break
            page += 1
        return responses

    @override
    def get_parsable_items(self, source: list[gruel.Response]) -> list[Tag]:
        event_blocks: list[Tag] = []
        for response in source:
            soup = response.get_soup()
            event_blocks.extend(soup.find_all("div", class_="event-info-block"))
        return event_blocks


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
