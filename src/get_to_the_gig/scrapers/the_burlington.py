import datetime
import json

import gruel
from bs4 import Tag
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel
from get_to_the_gig.squarespace import SquarespaceCalendar

# calendar url: https://www.theburlingtonbar.com


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:  # change `Any` to appropriate type
        return self._item

    # Add `_parse_` functions below
    def _parse_all(self) -> None:
        self.event.title = self.item["title"]
        self.event.acts = self.event.title
        self.event.date = datetime.datetime.fromtimestamp(
            int(self.item["startDate"] / 1000)
        )
        self.event.url = f"{self.event.venue.calendar_url}/{self.item['fullUrl']}"
        self.event.price = "$10"


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
    def get_parsable_items(self, source: gruel.Response) -> list[dict[str, Any]]:
        soup = source.get_soup()
        block = soup.find("div", class_="sqs-block calendar-block sqs-block-calendar")
        if not isinstance(block, Tag):
            raise exceptions.MissingElementError(
                "<div class='sqs-block calendar-block sqs-block-calendar'>"
            )
        collection_id = json.loads(str(block.get("data-block-json")))["collectionId"]
        return SquarespaceCalendar(
            gruel.models.Url(self.venue.url), collection_id, self.logger
        ).get_events()


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
