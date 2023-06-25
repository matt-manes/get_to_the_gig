from dataclasses import asdict, dataclass

import dacite
from pathier import Pathier, Pathish
from typing_extensions import Self


@dataclass
class Config:
    dbpath: str
    backup_before_scrape: bool
    drop_future_events: bool
    update_in_the_future: bool
    drop_all_events: bool

    @classmethod
    def load(cls, path: Pathish = Pathier(__file__).parent / "config.toml") -> Self:
        """Return a `datamodel` object populated from `path`."""
        data = Pathier(path).loads()
        return dacite.from_dict(cls, data)

    def dump(self, path: Pathish = Pathier(__file__).parent / "config.toml"):
        """Write the contents of this `datamodel` object to `path`."""
        data = asdict(self)
        Pathier(path).dumps(data)
