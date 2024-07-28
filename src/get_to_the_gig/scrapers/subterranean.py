from datetime import datetime

import beat_kitchen
import gruel
from bs4 import Tag
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel

# calendar url: https://www.subt.net


class EventParser(beat_kitchen.EventParser):  # type: ignore
    @override
    def _parse_price(self) -> None:  # type: ignore
        price_span = self.item.find("span", class_="price")  # type: ignore
        if not isinstance(price_span, Tag):
            self.event.price = "See ticket url"  # type: ignore
            return
        self.event.price = price_span.text  # type: ignore


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    # Default requests `venue.calendar_url` and returns the response
    # Uncomment and override if needed
    # @override
    # def get_source(self) -> gruel.Response:
    #    raise NotImplementedError

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[Any]:
        ul = source.get_soup().find("ul", attrs={"id": "filtered-events-list"})
        if not isinstance(ul, Tag):
            raise exceptions.MissingElementError(
                '<ul id="filtered-events-list" class="seetickets-list-events grid-container display-flex">'
            )
        return ul.find_all("li")


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
