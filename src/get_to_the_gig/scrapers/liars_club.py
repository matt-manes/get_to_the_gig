from datetime import datetime

import gruel
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser
from get_to_the_gig.giggruel import GigGruel

# calendar url: https://cdn5.editmysite.com/app/store/api/v28/editor/users/131312941/sites/715381155365579768/products?per_page=60&categories[]=11eb8686dd0a0704b0c60cc47a2b63cc


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:
        return self._item

    # Add `_parse_` functions below
    def _parse_date(self) -> None:
        details = self.item["product_type_details"]
        self.event.date = datetime.strptime(
            f"{details['start_date']} {details['start_time']}", "%Y-%m-%d %H:%M %p"
        )

    def _parse_title(self) -> None:
        self.event.title = self.item["name"]

    def _parse_price(self) -> None:
        prices = self.item["price"]
        high = prices["high_formatted"]
        low = prices["low_formatted"]
        if high == low:
            self.event.price = high
        else:
            self.event.price = f"{low}-{high}"

    def _parse_urls(self) -> None:
        self.event.url = f"{self.event.venue.url}/{self.item['site_link']}"
        self.event.ticket_url = self.event.url


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
        return source.json()["data"]


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
