from datetime import datetime
from pathlib import Path

from databased import DataBased


def clear_old_events():
    """Updates the "in_the_future" column of past events to 0."""
    with DataBased(Path(__file__).parent / "shows.db") as db:
        events = db.get_rows("events", [("in_the_future", 1)])
        for event in events:
            if datetime.today() > event["date"]:
                db.update("events", "in_the_future", 0, event)


if __name__ == "__main__":
    clear_old_events()
