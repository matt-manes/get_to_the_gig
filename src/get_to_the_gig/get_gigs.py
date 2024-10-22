from dataclasses import asdict

import gruel
import quickpool
from pathier import Pathier
from printbuddies import Grid
from rich import print
from typing_extensions import Any, Sequence, Type

from get_to_the_gig.giggruel import GigGruel

root = Pathier(__file__).parent


class Brewer(gruel.Brewer):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.executed_scrapers: list[GigGruel] = []

    def scrape(self) -> list[Any]:
        """Run the `scrape()` method for each scraper in `scrapers`.

        Execution is multithreaded."""

        def execute(
            scraper_class: Type[GigGruel], args: Sequence[Any], kwargs: dict[str, Any]
        ):
            scraper = scraper_class(*args, **kwargs)
            self.executed_scrapers.append(scraper)
            return scraper.scrape()

        pool = quickpool.ThreadPool(
            [execute] * len(self.scrapers), self._prep_scrapers()
        )
        return pool.execute()


def main():
    """ """
    brewer = Brewer(
        gruel.GruelFinder(
            ["VenueScraper"], ["*template.py"], scan_path=root / "scrapers"
        ).find()
    )
    results = brewer.brew()
    print(
        Grid(
            [
                {
                    "Venue": scraper.venue.name,
                    "Successes": str(scraper.success_count),
                    "Failures": str(scraper.fail_count),
                    "New Events": str(len(scraper.newly_added_events)),
                }
                for scraper in brewer.executed_scrapers
            ],
            cast_values_to_strings=True,
        )
    )
    input("...")


if __name__ == "__main__":
    main()
