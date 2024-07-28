from datetime import datetime

import gruel
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel

# calendar url: https://www.emptybottle.com


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:  # change `Any` to appropriate type
        return self._item

    # Add `_parse_` functions below
    def _parse_title(self) -> None:
        self.event.title = self.item["name"]

    def _parse_url(self) -> None:
        self.event.url = self.item["url"]
        self.event.ticket_url = self.event.url

    def _parse_acts(self) -> None:
        self.event.acts = self.item["name"]

    def _parse_date(self) -> None:
        start = self.item["dates"]["start"]
        self.event.date = datetime.strptime(
            f"{start['localDate']} {start['localTime']}", "%Y-%m-%d %H:%M:%S"
        )

    def _parse_price(self) -> None:
        prices = self.item["priceRanges"][0]
        if prices["min"] == prices["max"]:
            self.event.price = f"${prices['min']:.2f}"
        else:
            self.event.price = f"${prices['min']:.2f}-${prices['max']:.2f}"

    def _parse_age_restriction(self) -> None:
        self.event.age_restriction = "21+"


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    @property
    def api_url(self) -> str:
        return "https://app.ticketmaster.com/discovery/v2/events.json?size=200&apikey=GmC9AB6l4pDhA5yhg4dgD3G0AEDK8wmL&venueId=KovZpZAId16A&venueId=rZ7HnEZ178O8A&venueId=rZ7HnEZ17a4Af&venueId=KovZ917AEIJ&venueId=KovZ917AEEX&venueId=KovZpZAFJ1EA&venueId=KovZpZAFEFAA&venueId=KovZpaptBe&venueId=KovZpaptYe&venueId=KovZpZAkt67A&venueId=KovZ917AEIJ"

    # Default requests `venue.calendar_url` and returns the response
    # Uncomment and override if needed
    @override
    def get_source(self) -> gruel.Response:
        return self.request(self.api_url)

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[dict[str, Any]]:
        return source.json()["_embedded"]["events"]


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
