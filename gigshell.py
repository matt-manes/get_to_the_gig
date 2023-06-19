from argshell import ArgShellParser, Namespace, with_parser
from pathier import Pathier

from databased import DataBased, DBShell, dbparsers
from gigbased import GigBased
import models
from datetime import datetime

root = Pathier(__file__).parent


def add_venue_parser() -> ArgShellParser:
    parser = ArgShellParser()
    parser.add_argument("name", type=str)
    parser.add_argument("website", type=str)
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


def add_venue_post(args: Namespace) -> Namespace:
    """Post parser for `add_venue_parser()`."""
    if not args.calendar_url:
        args.calendar_url = args.website
    args.website = args.website.strip("/")
    args.calendar_url = args.calendar_url.strip("/")
    return args


class Gigshell(DBShell):
    intro = "Starting gigshell (enter help or ? for command info)..."
    prompt = "gigshell>"
    dbpath: Pathier = Pathier("getToTheGig.db")
    db = GigBased(dbpath)

    @with_parser(add_venue_parser, [add_venue_post])
    def do_add_venue(self, args: Namespace):
        """Add venue to database."""
        venue = models.Venue(
            args.name,
            models.Address(args.street, args.city, args.state, args.zipcode),
            args.website,
            args.calendar_url,
            datetime.now(),
        )
        if self.db.venue_in_database(venue):
            print("ERROR: This venue is already in the database.")
        else:
            successful = self.db.add_venue(venue)
            self.db.close()
            if not successful:
                print(f"ERROR adding venue.\nSee {self.dbpath.stem}.log for details.")
            else:
                print(f"{args.name} successfully added to the database.")
                template = (root / "scrapers" / "template.py").read_text()
                template = template.replace(
                    "# calendar url:", f"# calendar url: {venue.calendar_url}"
                )
                template = template.replace(
                    "Venue",
                    "".join(word.capitalize() for word in venue.ref_name.split("_")),
                )
                (root / "scrapers" / f"{venue.ref_name}.py").write_text(template)


if __name__ == "__main__":
    Gigshell().cmdloop()
