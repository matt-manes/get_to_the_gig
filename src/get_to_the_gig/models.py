from dataclasses import dataclass, fields
from datetime import datetime

from typing_extensions import Optional, Self, override


@dataclass
class Venue:
    venue_id: int
    name: str
    ref: str
    street: str
    city: str
    state: str
    zip_code: str
    url: str
    calendar_url: str
    date_added: datetime

    def __str__(self) -> str:
        return "\n".join([self.name, self.calendar_url, str(self.address)])

    @property
    def address(self) -> str:
        """Returns a string representation of the venue's address."""
        return f"{self.street}\n{self.city}, {self.state}\n{self.zip_code}"


@dataclass
class Event:
    """
    Fields:
    * title
    * date
    * acts
    * price
    * url
    * ticket_url
    * act_urls
    * info
    * age_restriction
    """

    event_id: int
    venue: Venue
    date_added: datetime
    title: str = ""
    date: Optional[datetime] = None
    acts: str = ""
    price: str = ""
    url: str = ""
    ticket_url: str = ""
    act_urls: str = ""
    info: str = ""
    age_restriction: str = ""

    @override
    def __eq__(self, value: object) -> bool:
        # TODO: Make this better, many times the url will change if the lineup changes
        # may need to create multiple venue entries for venues with split spaces, like upstairs and downstairs
        # then `venue_id` and `date` should be sufficient.
        if isinstance(value, self.__class__):
            return (
                self.venue.venue_id == value.venue.venue_id
                and self.date == value.date
                and (self.url == value.url)
                and (self.ticket_url == value.ticket_url)
            )
        raise TypeError(f"Can only compare other `Event` objects, not `{type(value)}`.")

    @property
    def in_the_future(self) -> bool:
        """Whether this event has already happened or not.

        Returns `False` if event has no listed date.
        """
        return datetime.now() > self.date if self.date else False

    def dump(self) -> str:
        """Dump field names and values. Primarily for debugging and crash logs."""
        members = sorted(fields(self), key=lambda field: field.name)
        return "\n".join(
            (f"'{member.name}': '{getattr(self, member.name)}'" for member in members)
        )

    @classmethod
    def new(cls, venue: Venue) -> Self:
        return cls(-1, venue, datetime.now())

    def trim(self) -> None:
        """Trim excess whitespace from string fields and trailing slashes from urls."""
        for field in fields(self):
            if isinstance(field, str):
                setattr(self, field, getattr(self, field).strip())
        self.url = self.url.strip("/")
        self.ticket_url = self.ticket_url.strip("/")

    def validate_year(self) -> None:
        """
        If the event date looks to be more than 30 days in the past, increase the year by 1.

        Only necessary on venues that don't list the year for events.

        e.g. it's currently December and the event is in January,
        but no year listed may result in a datetime for January of this year instead of next year.

        Use of this function assumes the venue removes previous events from their website within 30 days after the event.
        """
        if not self.date:
            return
        if (datetime.now() - self.date).days > 30:
            self.date = self.date.replace(year=self.date.year + 1)
