import datetime

import gruel
import loggi
from typing_extensions import Any, Iterable


class MonthTracker:
    def __init__(self, max_months: int = 12):
        self._date: datetime.datetime = datetime.datetime.now()
        self._counter: int = 1
        self._max_months = max_months

    def advance(self) -> None:
        self._date = self._date.replace(day=15) + datetime.timedelta(weeks=4)
        self._counter += 1

    def each_month(self) -> Iterable[datetime.datetime]:
        while self._counter <= self._max_months:
            yield self._date
            self.advance()


class SquarespaceCalendar:
    def __init__(
        self,
        venue_url: gruel.models.Url,
        collection_id: str,
        logger: loggi.Logger | None = None,
    ) -> None:
        self.venue_url: gruel.models.Url = venue_url
        self.collection_id: str = collection_id
        self.logger = logger

    def get_events_by_month_endpoint(self, date: datetime.datetime) -> gruel.models.Url:
        """The month and year represented by `date` will be used to return the appropriate end point url."""
        url: gruel.models.Url = self.venue_url
        url.path = "api/open/GetItemsByMonth"
        url.query = f"month={date:%m-%Y}&collectionId={self.collection_id}"
        return url

    def get_events(self, max_months: int = 12) -> list[dict[str, Any]]:
        """Fetch and return events from the current month until `max_months` from now or until no events are returned."""
        month_tracker = MonthTracker(max_months)
        events: list[dict[str, Any]] = []
        for month in month_tracker.each_month():
            endpoint = self.get_events_by_month_endpoint(month)
            if not (
                content := gruel.request(endpoint.address, logger=self.logger).json()
            ):
                break
            events.extend(content)
        return events
