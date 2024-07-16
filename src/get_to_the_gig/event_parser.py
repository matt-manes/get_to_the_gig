from typing_extensions import Any

from get_to_the_gig import models


class EventParser:
    """Parse an event into an event model by subclassing this class
    and adding methods that have `_parse_` prefixed to their name.

    All of these methods will be called sequentially when `parse()` is called.

    These methods should take no arguments and return nothing.

    e.g. methods:
        * `def _parse_date_(self)->None` to parse and store the event into `self.event`
        * `def _parse_acts(self)->None` to parse and store the acts into `self.event`
    """

    def __init__(self, venue: models.Venue, item: Any):
        self.event = models.Event.new(venue)
        self._item = item

    @property
    def item(self) -> Any:
        """Returns the event item.

        Override to specify type annotation."""
        return self._item

    def _loop_parsers(self) -> None:
        """Loop over instance and call any methods that start with `_parse_`.

        These methods should take no arguments and return `None`."""
        for attr in self.__dir__():
            if attr.startswith("_parse_"):
                getattr(self, attr)()

    def parse(self) -> models.Event:
        self._loop_parsers()
        return self.event
