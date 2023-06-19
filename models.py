import re
import string
from dataclasses import dataclass
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
    website: str
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


@dataclass
class Event:
    venue: Optional[str | Venue] = ""
    title: Optional[str] = ""
    date: Optional[datetime] = datetime.now()
    acts: Optional[str] = ""
    price: Optional[str] = ""
    event_url: Optional[str] = ""
    ticket_url: Optional[str] = ""
    act_urls: Optional[str] = ""
    info: Optional[str] = ""
    age_restriction: Optional[str] = ""
    date_added: Optional[datetime] = datetime.now()
    genres: Optional[str] = ""
    in_the_future: Optional[bool] = True

    @classmethod
    def new(cls) -> Self:
        return cls(date_added=datetime.now(), in_the_future=True)
