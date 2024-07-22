import re
from datetime import datetime

import gruel
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser
from get_to_the_gig.giggruel import GigGruel
from get_to_the_gig.squarespace import SquarespaceCalendar


# calendar url: https://elasticarts.org/events
class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:
        return self._item

    # Add `_parse_` functions below
    def _parse_all(self) -> None:
        self.event.date = datetime.fromtimestamp(int(self.item["startDate"] / 1000))
        self.event.title = self.item["title"]
        self.event.price = "$15+"
        self.event.url = f"{self.event.venue.url}/{self.item['fullUrl']}"


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
        collection_id = re.findall(
            r'collectionId":"[a-zA-Z0-9]+"', source.text.replace("&quot;", '"')
        )[0].split('"')[2]
        return SquarespaceCalendar(
            gruel.models.Url(self.venue.url), collection_id, self.logger
        ).get_events()


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
