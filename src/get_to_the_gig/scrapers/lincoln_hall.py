import json
from datetime import datetime
from functools import cached_property

import gruel
from bs4 import BeautifulSoup, Tag
from typing_extensions import Any, Type, override

from get_to_the_gig import event_parser, exceptions, utilities
from get_to_the_gig.giggruel import GigGruel

# calendar url: https://lh-st.com


class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> BeautifulSoup:  # change `Any` to appropriate type
        return self._item

    @cached_property
    def artists_div(self) -> Tag:
        artists_div = self.item.find("div", class_="tessera-artists")
        if not isinstance(artists_div, Tag):
            raise exceptions.MissingElementError("<div class='tessera-artists'>")
        return artists_div

    @cached_property
    def headliner(self) -> str:
        artists_div = self.artists_div
        h2 = artists_div.find("h2")
        if not isinstance(h2, Tag):
            raise exceptions.MissingElementError(
                "<h2>", "<div class='tessera-artists'>"
            )
        return h2.text.strip(", ")

    @cached_property
    def script_data(self) -> dict[str, str]:
        body = self.item.find("body")
        if not isinstance(body, Tag):
            raise exceptions.MissingElementError("<body>")
        script = body.find("script")
        if not isinstance(script, Tag):
            raise exceptions.MissingElementError("<script>")
        return utilities.load_js_dict(script.text)

    @cached_property
    def id_(self) -> str:
        return self.script_data["eventID"]

    @property
    def session_id(self) -> str:
        return "RUFBQUFCZ09pMGsxM1cwTjkzMXFTM0ZXN2lTT2RDMG5ISWd0SmxyTTRLZmpGcFZmQS8xNmZocXpIdVU1U015NGJwWlQ1T0E4ZXJGK0RWT2cyNHAybGxtT0x0UT0="

    @cached_property
    def api_url(self) -> str:
        return f"https://tickets.lh-st.com/api/v1/products/{self.id_}"

    @cached_property
    def yoast_schema(self) -> dict[Any, Any]:
        script = self.item.find(
            "script", class_="yoast-schema-graph", attrs={"type": "application/ld+json"}
        )
        if not isinstance(script, Tag):
            raise exceptions.MissingElementError(
                "<script type='application/ld+json' class='yoast-schema-graph'"
            )
        return json.loads(script.text)

    # Add `_parse_` functions below
    def _parse_url(self) -> None:
        self.event.url = self.yoast_schema["@graph"][0]["url"].strip("/")

    def _parse_title(self) -> None:
        header_div = self.item.find("div", class_="event-header")
        header = header_div.text if isinstance(header_div, Tag) else ""
        self.event.title = f"{header} {self.headliner}"

    def _parse_acts(self) -> None:
        headliner = self.headliner
        additional_div = self.item.find("div", class_="additional-artists")
        if isinstance(additional_div, Tag):
            self.event.acts = f"{headliner}, {additional_div.text}"
        else:
            self.logger.info(
                f"Additional artists element not found for `{self.event.url}`."
            )
            self.event.acts = headliner
        self.event.acts = self.event.acts.replace("\n", "").strip(", ")

    def _parse_date(self) -> None:
        if "dateandTime" not in self.script_data:
            self.logger.warning(
                f"No `dateandTime` key in `script_data` for `{self.event.url}`."
            )
            return
        self.event.date = datetime.strptime(
            self.script_data["dateandTime"], "%m/%d/%Y %I:%M %p"
        )

    def _parse_age_restriction(self) -> None:
        age_div = self.item.find("div", class_="ages")
        if not age_div:
            self.logger.warning(
                f"Age restriction element not found for `{self.event.url}`."
            )
            return
        self.event.age_restriction = age_div.text.strip()

    def _get_price_from_api(self) -> str:
        response = gruel.request(
            self.api_url, headers={"SessionId": self.session_id}, logger=self.logger
        )
        response.raise_for_status()
        if response.status_code == 204:
            return "Free"
        data = response.json()
        return "|".join(
            f"{ticket['name']}: ${ticket['price']:.2f}" for ticket in data["campaigns"]
        )

    def _parse_price(self) -> None:
        tickets_a = self.item.find("a", string="GET TICKETS")
        if isinstance(tickets_a, Tag):
            self.event.price = "?"
            self.event.ticket_url = str(tickets_a.get("href"))
            return
        # If the above wasn't found, go to the end point
        self.event.ticket_url = self.event.url
        self.event.price = self._get_price_from_api()


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

    def _get_event_urls(self, soup: BeautifulSoup) -> list[str]:
        return [
            div.find("a").get("href")
            for div in soup.find_all(
                "div", class_="card-footer text-start align-items-center"
            )
            if self.venue.name.split()[0] in div.find("span").text
        ]

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[BeautifulSoup]:
        soup = source.get_soup()
        urls = self._get_event_urls(soup)
        return [response.get_soup() for response in self._get_pages(urls)]


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
