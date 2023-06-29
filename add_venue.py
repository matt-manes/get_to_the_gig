from datetime import datetime

from pathier import Pathier

import exceptions
import models
from gigbased import GigBased

root = Pathier(__file__).parent


def create_from_template(venue: models.Venue):
    """Create a scraper file in scrapers folder for `venue` from `template.py`."""
    template_path = root / "scrapers" / "template.py"
    template = template_path.read_text()
    template = template.replace(
        "# calendar url:", f"# calendar url: {venue.calendar_url}"
    )
    (template_path.with_stem(venue.ref_name)).write_text(template)


def add_venue(venue: models.Venue) -> bool:
    """Add `venue` to the database and generate scraper template.

    Raises an `exceptions.VenueExistsError` exception if `venue` is already in the database.

    Returns `True` if database transaction was successful."""

    venue.url = venue.url.strip("/")
    venue.calendar_url = venue.calendar_url.strip("/")
    with GigBased() as db:
        if db.venue_in_database(venue):
            raise exceptions.VenueExistsError(venue.name)
        return db.add_venue(venue)
