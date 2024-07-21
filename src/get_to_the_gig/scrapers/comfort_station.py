import re
from datetime import datetime

import gruel
from bs4 import Tag
from pathier import Pathier
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel
from get_to_the_gig.squarespace import SquarespaceCalendar

# calendar url: https://comfortstationlogansquare.org/calendar


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:
        return self._item

    def _parse_all(self) -> None:
        self.event.title = self.item["title"]
        self.event.date = datetime.fromtimestamp(int(self.item["startDate"] / 1000))
        self.event.url = f"{self.event.venue.calendar_url}/{self.item['urlId']}"
        self.event.price = "Donations Encouraged"


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[dict[str, Any]]:
        collection_id = re.findall(r'data-collection-id="[a-zA-Z0-9]+"', source.text)[
            0
        ].split('"')[1]
        return SquarespaceCalendar(
            gruel.models.Url(self.venue.url), collection_id, self.logger
        ).get_events()


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
