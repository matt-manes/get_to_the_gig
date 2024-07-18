import re
from datetime import datetime, timedelta

import gruel
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel

# calendar url: https://cobralounge.com/events


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> dict[str, Any]:
        return self._item

    def _parse_date(self) -> None:
        self.event.date = datetime.strptime(
            self.item["date"], "%Y-%m-%dT%H:%M:%SZ"
        ) - timedelta(hours=5)

    def _parse_title(self) -> None:
        self.event.title = self.item["name"]

    def _parse_acts(self) -> None:
        self.event.acts = ", ".join(self.item["artists"])

    def _parse_price(self) -> None:
        if self.item["ticket_types"]:
            self.event.price = (
                f"${self.item['ticket_types'][0]['price']['total']/100:.2f}"
            )
        else:
            try:
                self.event.price = f"${self.item['price']/100:.2f}"
            except Exception as e:
                self.event.price = "n/a"

    def _parse_urls(self) -> None:
        self.event.url = self.item["url"]
        self.event.ticket_url = self.event.url

    def _parse_age_restriction(self) -> None:
        self.event.age_restriction = self.item["age_limit"]


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[dict[str, Any]]:
        api_key = re.findall(r'"apiKey":"[a-zA-Z0-9]+"', source.text)[0]
        api_key = api_key.split(":")[1].strip('"')
        response = self.request(
            "https://events-api.dice.fm/v1/events?page[size]=100&types=linkout,event&filter[venues][]=Cobra%20Lounge",
            headers={"x-api-key": api_key},
        )
        return [event for event in response.json()["data"] if event["raw_description"]]


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
