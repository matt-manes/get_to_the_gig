import re
import string
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from typing_extensions import Self


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
    reference: str = ""  # Scraper files will be named with this + `.py`

    def __post_init__(self):
        self.generate_reference()

    def generate_reference(self):
        """Generate reference name from instance's `name` member."""
        self.reference = (
            re.sub(rf"[{string.punctuation}]", "", self.name).replace(" ", "_").lower()
        )

    @classmethod
    def new(cls) -> Self:
        return cls("", Address.new(), "", "", datetime.now())


@dataclass
class Event:
    venue: Optional[str | Venue] = None
    title: Optional[str] = None
    date: Optional[datetime] = None
    acts: Optional[str] = None
    price: Optional[str] = None
    event_url: Optional[str] = None
    ticket_url: Optional[str] = None
    act_urls: Optional[str] = None
    info: Optional[str] = None
    age_restriction: Optional[str] = None
    date_added: Optional[datetime] = None
    genres: Optional[str] = None
    in_the_future: Optional[bool] = None

    @classmethod
    def new(cls) -> Self:
        return cls(date_added=datetime.now(), in_the_future=True)


if __name__ == "__main__":
    e = Event.new()
    print(e)
