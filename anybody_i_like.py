from pathlib import Path

from databased import DataBased, data_to_string

root = Path(__file__).parent
acts_i_like = (root / "actsILike.txt").read_text().splitlines()

db = DataBased(root / "shows.db")
events = db.get_rows(
    "events",
    [("in_the_future", 1)],
    columns_to_return=["date", "venue", "acts", "price", "event_link"],
)
events_i_like = [
    event
    for event in events
    if any(act_i_like in event["acts"].lower() for act_i_like in acts_i_like)
]
if len(events_i_like) > 0:
    print(data_to_string(events_i_like))
else:
    print("nope, nobody you like :/")
