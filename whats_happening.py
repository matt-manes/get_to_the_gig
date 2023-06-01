import argparse
from datetime import datetime, timedelta
from pathier import Pathier

from databased import DataBased, data_to_string

from clear_old_events import clear_old_events
from griddle import griddy

root = Pathier(__file__).parent


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-da",
        "--days_away",
        nargs="*",
        default=[0],
        type=int,
        help=""" Expects one or two arguments.
        If one argument is passed, only events that many days away will be shown.
        If two arguments are passed, events within those many days, inclusive, will be shown.
        i.e. "-da 0 7" will show events between today and 7 days from now.""",
    )

    parser.add_argument(
        "-dotw",
        "--day_of_the_week",
        default=[],
        type=str,
        nargs="*",
        help=""" Show events by day of the week name.
        i.e. "-dotw friday" will show events for the upcoming friday.
        (If the current day is friday, it will show events for the following friday.)
        If today is tuesday and "-dotw friday thursday" is used, the results will events
        between friday and the thursday after this friday, inclusive.
        If this arg is provided alongside -da/--days_away, -da/--days_away will be ignored.""",
    )

    parser.add_argument(
        "-v",
        "--venues",
        type=str,
        default=None,
        nargs="*",
        help=""" Only show these venues in the results.
        Any venue names with spaces in it must be enclosed in quotes.""",
    )

    parser.add_argument(
        "-i", "--info", action="store_true", help="Show event info column in output."
    )

    parser.add_argument(
        "-sb",
        "--sort_by",
        type=str,
        default="date",
        help="Sort the output by this column.",
    )

    def get_days_away(day: str) -> int:
        today = datetime.today()
        for i in range(1, 8):
            if (today + timedelta(days=i)).strftime("%A").lower() == day.lower():
                return i

    args = parser.parse_args()

    if len(args.day_of_the_week) == 1:
        args.days_away = [get_days_away(args.day_of_the_week[0])]
    elif len(args.day_of_the_week) > 1:
        args.days_away = [
            get_days_away(args.day_of_the_week[0]),
            get_days_away(args.day_of_the_week[1]),
        ]
        if args.days_away[1] < args.days_away[0]:
            args.days_away[1] += 7

    if len(args.days_away) == 1:
        args.days_away.append(args.days_away[0])

    if args.venues:
        args.venues = [
            " ".join(word.capitalize() for word in venue.split())
            for venue in args.venues
        ]
    return args


if __name__ == "__main__":
    args = get_args()
    clear_old_events()
    columns_to_return = [
        "date",
        "venue",
        "acts",
        "price",
        "event_link",
    ]
    if args.info:
        columns_to_return.append("info")
    with DataBased("shows.db") as db:
        if not args.venues:
            future_events = db.get_rows(
                "events",
                [("in_the_future", 1)],
                columns_to_return=columns_to_return,
                order_by=args.sort_by,
            )
        else:
            future_events = [
                row
                for venue in args.venues
                for row in db.get_rows(
                    "events",
                    [("in_the_future", 1), ("venue", venue)],
                    columns_to_return=columns_to_return,
                    order_by=args.sort_by,
                )
            ]
    filtered_events = []
    today = datetime.today()
    date_range = (
        today.replace(hour=0, minute=0, second=0, microsecond=0)
        + timedelta(days=args.days_away[0]),
        today.replace(hour=23, minute=59, second=59, microsecond=999999)
        + timedelta(days=args.days_away[1]),
    )
    for event in future_events:
        if date_range[0] <= event["date"] and event["date"] <= date_range[1]:
            filtered_events.append(event)

    if filtered_events:
        print(griddy(filtered_events, headers="keys"))
    else:
        print("Nothing happening :(")
