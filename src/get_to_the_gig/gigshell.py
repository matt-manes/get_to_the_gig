import shlex

from argshell import ArgShellParser, Namespace, with_parser
from databased.dbshell import DBShell
from pathier import Pathier

from get_to_the_gig import utilities
from get_to_the_gig.config import Config
from get_to_the_gig.gigbased import Gigbased

root = Pathier(__file__).parent


def add_venue_parser() -> ArgShellParser:
    parser = ArgShellParser()
    parser.add_argument("name", type=str)
    parser.add_argument("url", type=str)
    parser.add_argument(
        "-cal",
        "--calendar_url",
        type=str,
        default=None,
        help=""" The venue's calendar url, if different from it's main website url. """,
    )
    parser.add_argument("-s", "--street", type=str, default="")
    parser.add_argument("-c", "--city", type=str, default="Chicago")
    parser.add_argument(
        "-st",
        "--state",
        type=str,
        default="IL",
        help=""" Two letter state abbreviation. """,
    )
    parser.add_argument("-z", "--zipcode", type=str, default="")
    return parser


def events_parser() -> ArgShellParser:
    with Gigbased() as db:
        venues = [venue.name for venue in db.get_venues()]
    parser = ArgShellParser()
    parser.add_argument(
        "days_away",
        type=int,
        nargs="*",
        default=None,
        help=""" Show events that are this many days away from now.
            If only one value is given, only events on that day will be shown.
            If two are given, events within that range will be shown.
            If nothing is given, all events will be shown.""",
    )
    parser.add_argument(
        "-v",
        "--venues",
        type=str,
        nargs="*",
        choices=venues,
        default=None,
        help=""" Optional list of venues to filter events with. """,
    )
    return parser


class Gigshell(DBShell):
    intro = "Starting gigshell (enter help or ? for command info)..."
    prompt = "gigshell>"
    _dbpath: Pathier = root / "data" / "get_to_the_gig.db"
    db = Gigbased(_dbpath)

    def do_init(self, _: str) -> None:
        """Initialize database."""
        sql_dir = root / "sql"
        with Gigbased(self._dbpath) as db:
            for file in ("schema.sql", "views.sql", "venues_data.sql"):
                db.execute_script(sql_dir / file)

    # @with_parser(add_venue_parser)
    # def do_add_venue(self, args: Namespace):
    #    """Add venue to database."""
    #    venue = models.Venue(
    #        args.name,
    #        models.Address(args.street, args.city, args.state, args.zipcode),
    #        args.url,
    #        args.calendar_url or args.url,
    #        datetime.now(),
    #    )
    #    try:
    #        success_status = add_venue.add_venue(venue)
    #    except Exception as e:
    #        print(e)
    #    else:
    #        if not success_status:
    #            print(f"ERROR adding venue.\nSee {self.dbpath.stem}.log for details.")
    #        else:
    #            add_venue.create_from_template(venue)
    #            print(f'"{venue.name}" successfully added to database.')
    #            print(
    #                f'Template scraper class has been generated and is located at "scrapers/{venue.ref_name}.py".'
    #            )

    def do_scraper_ready(self, args: str):
        """Set `scraper_ready` to `True` in the database for these venues."""
        venues = shlex.split(args)
        updates = 0
        with Gigbased() as db:
            for venue in venues:
                updates += db.update("venues", "scraper_ready", 1, f"name = '{venue}'")
        print(f"Updated {updates} venues.")

    @with_parser(events_parser)
    def do_events(self, args: Namespace):
        """Show events."""
        if not args.days_away:
            date_clause = 1
        else:
            start, stop = utilities.get_days_away_daterange(
                (
                    args.days_away[0],
                    (
                        args.days_away[0]
                        if len(args.days_away) == 1
                        else args.days_away[1]
                    ),
                )
            )
            date_clause = f"date BETWEEN '{start}' AND '{stop}'"
        venue_clause = (
            1 if not args.venues else "venue in ('" + "', '".join(args.venues) + "')"
        )
        config = Config.load()
        columns = ", ".join(config.default_event_column_order)
        query = f"SELECT {columns} FROM events WHERE {venue_clause} AND {date_clause} ORDER BY date;"
        with Gigbased() as db:
            events = db.query(query)
        print(db.to_grid(events))


def main():
    Gigshell().cmdloop()


if __name__ == "__main__":
    main()
