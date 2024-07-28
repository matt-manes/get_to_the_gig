from datetime import datetime

import gruel
from bs4 import Tag
from typing_extensions import Type, override

from get_to_the_gig import event_parser, exceptions
from get_to_the_gig.giggruel import GigGruel


# calendar url: https://www.beatkitchen.com
class EventParser(event_parser.EventParser):
    @property
    @override
    def item(self) -> Tag:
        return self._item

    def _parse_title_tag(self) -> None:
        a_event_title = self.item.find("a", attrs={"target": "_blank"})
        if not isinstance(a_event_title, Tag):
            self.logger.warning("Could not find title element.")
            return
        self.event.title = a_event_title.text
        self.event.ticket_url = a_event_title.attrs["href"]
        self.event.url = self.event.ticket_url

    def _parse_acts(self) -> None:
        p_headliners = self.item.find("p", class_="fs-12 headliners")
        if not isinstance(p_headliners, Tag):
            self.logger.warning("Could not find headliners element.")
            return
        headliner = p_headliners.text.strip()
        p_supporting = self.item.find("p", class_="fs-12 supporting-talent")
        if not isinstance(p_supporting, Tag) or p_supporting.text.strip() == "":
            self.event.acts = headliner
        else:
            self.event.acts = f"{headliner}, {p_supporting.text.strip()}"

    def _parse_date(self) -> None:
        p_event_date = self.item.find("p", class_="fs-18 bold mt-1r event-date")
        if not isinstance(p_event_date, Tag):
            self.logger.warning("Could not find date element.")
            return
        date = p_event_date.text
        # "day-name-abbrev month-name-abbbrev day-digit"
        date_format = "%a %b %d"
        span_time = self.item.find("span", class_="event-time")
        if isinstance(span_time, Tag):
            # "Show: x:xx XM"
            show_time = span_time.text.removeprefix("Show:")
            date += show_time
            date_format += " %I:%M %p"
        self.event.date = datetime.strptime(date, date_format)
        self.event.date = self.event.date.replace(year=datetime.now().year)
        self.event.validate_year()

    def _parse_price(self) -> None:
        self.event.price = "See ticket url"

    def _parse_age_restriction(self) -> None:
        span_ages = self.item.find("span", class_="ages")
        if not isinstance(span_ages, Tag):
            self.logger.warning("Could not find age restriction element.")
            return
        self.event.age_restriction = span_ages.text.strip(", ")


class VenueScraper(GigGruel):
    @property
    @override
    def event_parser(self) -> Type[EventParser]:
        return EventParser

    @override
    def get_parsable_items(self, source: gruel.Response) -> list[Tag]:
        list_view = source.get_soup().find("div", class_="list-view-events")
        if not isinstance(list_view, Tag):
            raise exceptions.MissingSourceError(self.venue.name)
        return list_view.find_all("div", class_="event-info-block")


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
