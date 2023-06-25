import re
import string
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from typing import Optional

from typing_extensions import Self, Any


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str

    def __str__(self) -> str:
        return f"{self.street}\n{self.city}, {self.state}\n{self.zip_code}"

    @classmethod
    def new(cls) -> Self:
        return cls("", "Chicago", "IL", "")


@dataclass
class Venue:
    name: str
    address: Address
    url: str
    calendar_url: str
    date_added: datetime
    # Scraper files will be named with this + `.py`
    # The scraper class should also be named this, but camel case
    ref_name: str = ""

    def __post_init__(self):
        if not self.ref_name:
            self.generate_ref_name()

    def generate_ref_name(self):
        """Generate reference name from instance's `name` member."""
        self.ref_name = (
            re.sub(rf"[{string.punctuation}]", "", self.name).replace(" ", "_").lower()
        )

    @classmethod
    def new(cls) -> Self:
        return cls("", Address.new(), "", "", datetime.now())

    def __str__(self) -> str:
        return "\n".join(
            [
                self.name,
                self.calendar_url,
                str(self.address),
            ]
        )

    @property
    def flattened_dict(self) -> dict[str, Any]:
        """Returns same thing as `dataclasses.asdict()`, except `self.address` will be extracted to the top layer.

        i.e.
        >>> d = venue.flattened_dict
        >>> d["state"]
        >>> "IL"
        instead of
        >>> d["address"]["state"]"""
        addy = asdict(self.address)
        venue = asdict(self)
        venue.pop("address")
        venue |= addy
        return venue


@dataclass
class Event:
    venue: Optional[str | Venue] = ""
    title: Optional[str] = ""
    date: Optional[datetime] = None
    acts: Optional[str] = ""
    price: Optional[str] = ""
    url: Optional[str] = ""
    ticket_url: Optional[
        str
    ] = ""  # Sometimes the ticketing page is separate from the venue's event page
    act_urls: Optional[str] = ""
    info: Optional[str] = ""
    age_restriction: Optional[str] = ""
    date_added: Optional[datetime] = datetime.now()
    genres: Optional[str] = ""
    in_the_future: Optional[bool] = True

    def dump(self) -> str:
        """Dump field names and values. Primarily for debugging and crash logs."""
        members = sorted(fields(self), key=lambda field: field.name)
        return "\n".join(
            f"{member.name}: {getattr(self, member.name)}" for member in members
        )

    @classmethod
    def new(cls) -> Self:
        return cls(date_added=datetime.now(), in_the_future=True)

    def clean(self):
        """Strip ` \n\t\r` characters and remove `"` characters from `str` members."""
        for field in fields(self):
            name = field.name
            val = getattr(self, name)
            if type(val) is str:
                setattr(self, name, val.strip(" \n\t\r").replace('"', ""))
