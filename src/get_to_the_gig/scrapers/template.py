from datetime import datetime

import gruel
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel

# calendar url: ${calendar_url}


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> Any:  # change `Any` to appropriate type
        return self._item

    # Add `_parse_` functions below
    # def _parse_NAME(self) -> None:


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
        raise NotImplementedError


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
