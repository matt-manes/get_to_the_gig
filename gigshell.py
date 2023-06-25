from datetime import datetime

from argshell import ArgShellParser, Namespace, with_parser
from databased import DataBased, DBShell, dbparsers
from pathier import Pathier

import add_venue
import models
from gigbased import GigBased

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


class Gigshell(DBShell):
    intro = "Starting gigshell (enter help or ? for command info)..."
    prompt = "gigshell>"
    dbpath: Pathier = Pathier("getToTheGig.db")
    db = GigBased(dbpath)

    @with_parser(add_venue_parser)
    def do_add_venue(self, args: Namespace):
        """Add venue to database."""
        venue = models.Venue(
            args.name,
            models.Address(args.street, args.city, args.state, args.zipcode),
            args.url,
            args.calendar_url or args.website,
            datetime.now(),
        )
        try:
            success_status = add_venue.add_venue(venue)
        except Exception as e:
            print(e)
        else:
            if not success_status:
                print(f"ERROR adding venue.\nSee {self.dbpath.stem}.log for details.")
            else:
                add_venue.create_from_template(venue)
                print(f'"{venue.name}" successfully added to database.')
                print(
                    f'Template scraper class has been generated and is located at "scrapers/{venue.ref_name}.py".'
                )


if __name__ == "__main__":
    Gigshell().cmdloop()
