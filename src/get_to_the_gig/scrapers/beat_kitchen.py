import json
import re
from datetime import datetime

import gruel
from bs4 import BeautifulSoup, Tag
from pathier import Pathier
from typing_extensions import Any, override

root = Pathier(__file__).parent
(root.moveup("get_to_the_gig")).add_to_PATH()
print(root.moveup("get_to_the_gig"))

import models
from giggruel import GigGruel


# calendar url: https://www.beatkitchen.com/calendar
class VenueScraper(GigGruel):
    @override
    def get_source(self) -> gruel.Response:
        return self.request(self.venue.calendar_url)

    def make_jsonable(self, text: str) -> str:
        """Modify `text` so that it can be loaded by the json module."""
        # Fix all the quotes
        text = text[text.find(":") + 1 :].replace('"', '\\"').replace("'", '"')
        lines = [line.strip() for line in text.splitlines()]
        for i, line in enumerate(lines):
            if not line.startswith(("{", "}", "[", "]")):
                key, value = line.split(":", 1)
                lines[i] = f'"{key}":{value}'
        # Last curly brace has a trailing comma
        lines[-2] = "}"
        return "\n".join(lines)

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[dict[str, Any]]:
        # There's a script tag with all the calendar elements in a list of dictionaries format
        text = re.findall(r"events: \[[^\]]+\]", source.text)[0]
        if not text:
            raise RuntimeError(
                f"{self.name}: Failed to find script tag with calendar elements."
            )
        text = self.make_jsonable(text)
        return json.loads(text)

    def _get_event_soup(self, url: str) -> BeautifulSoup:
        """Return event page content as a `BeautifulSoup` object."""
        return self.request(url).get_soup()

    def _get_ticket_url(self, soup: BeautifulSoup) -> str | None:
        buy_box = soup.find("div", class_="tw-buy-box")
        if not buy_box:
            return
        url_tag = buy_box.find("a")
        if not url_tag:
            return
        if not isinstance(url_tag, Tag):
            return
        url = url_tag.get("href")
        if not isinstance(url, str):
            return
        url = gruel.models.Url(url)
        url.query = ""
        return url.fragmentless.address

    def _parse_event_page(self, event: models.Event) -> models.Event:
        """Parse `soup` into `event` and return `event`."""
        soup = self._get_event_soup(event.url)
        age_tag = soup.find("div", class_="tw-age-restriction")
        if age_tag:
            event.age_restriction = age_tag.text
        price_tag = soup.find("div", class_="tw-price")
        event.price = price_tag.text if price_tag else "Free"
        event.ticket_url = self._get_ticket_url(soup) or ""
        return event

    @override
    def parse_item(self, item: dict[str, Any]) -> models.Event:
        event = self.new_event()
        if date := item.get("start", None):
            event.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        event.title = item["title"]
        event.acts = item["title"]
        event.url = f"https://www.beatkitchen.com/event-details/{item['id']}"
        return self._parse_event_page(event)


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.success_count)
    print(venue.fail_count)
