from datetime import datetime

import gruel
from bs4 import Tag
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel

# calendar url: https://sleeping-village.com/events


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:
        return self._item

    # Add `_parse_` functions below
    def _parse_urls(self) -> None:
        self.event.url = self.item["permalink"].strip("/")
        if "ticket" in self.item:
            self.event.ticket_url = self.item["ticket"]["link"]
        else:
            self.event.ticket_url = self.event.url

    def _parse_title(self) -> None:
        self.event.title = self.item["title"]

    def _parse_date(self) -> None:
        try:
            self.event.date = datetime.strptime(
                self.item["dateTime"], "<span>%a, %b %d %H:%M%p<span>"
            )
        except Exception as e:
            self.event.date = datetime.strptime(
                self.item["dateTime"], "<span>%a, %b %d<span>"
            )
        self.event.date = self.event.date.replace(year=datetime.now().year)
        self.event.validate_year()

    def _parse_acts(self) -> None:
        if "lineup" in self.item:
            self.event.acts = ", ".join(
                act["title"] for act in self.item["lineup"]["standard"]
            )

    def _parse_price(self) -> None:
        self.event.price = self.item["fromPrice"].removeprefix("Tickets from ")

    def _parse_age_restriction(self) -> None:
        self.event.age_restriction = "21+"


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    # Default requests `venue.calendar_url` and returns the response
    # Uncomment and override if needed
    @override
    def get_source(self) -> list[gruel.Response]:
        responses: list[gruel.Response] = []
        api_url = "https://sleeping-village.com/api/plot/v1/listings?currentpage="
        page = 1
        while True:
            response = self.request(api_url + str(page))
            if response.text == "[]" or page > 12:
                return responses
            responses.append(response)
            page += 1

    @override
    def get_parsable_items(self, source: list[gruel.Response]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for response in source:
            items.extend(response.json())
        return items


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
