import importlib
import re
import time
from concurrent.futures import ThreadPoolExecutor

from gitbetter import Git
from pathier import Pathier
from printbuddies import ProgBar

from config import Config
from gigbased import GigBased

root = Pathier(__file__).parent
scrapers_dir = root / "scrapers"
scrapers_dir.add_to_PATH()
from gig_scraper import GigScraper


def get_scrapers() -> list[GigScraper]:
    """Return a list of scraper objects."""
    with GigBased() as db:
        ref_names = [
            venue.ref_name
            for venue in db.get_venues(match_criteria={"scraper_ready": 1})
        ]
    files = [scrapers_dir / f"{ref_name}.py" for ref_name in ref_names]
    return [
        importlib.import_module(str(scraper.stem)).VenueScraper() for scraper in files
    ]


def prescrape_chores():
    config = Config.load()
    if config.backup_before_scrape:
        Pathier(config.dbpath).backup()
    if config.drop_all_events:
        with GigBased() as db:
            db.drop_all_events()
    config.all_chores_off()
    config.dump()


def push_db():
    """Push databased to github."""
    git = Git()
    config = Config.load()
    git.commit_files([config.dbpath], "chore: update event calendar")
    git.push()


def postscrape_chores():
    config = Config.load()
    if config.vacuum_db:
        with GigBased() as db:
            print(f"Vacuuming freed up {Pathier.format_bytes(db.vacuum())} of space.")
    if config.push_db:
        print("Pushing database to remote...")
        push_db()
    config.all_chores_on()
    config.dump()


def stats(scrapers: list[GigScraper]) -> tuple[int, int]:
    """Returns a tuple containing total successes and total failures across all scrapers."""
    successes = 0
    failures = 0
    for scraper in scrapers:
        stats = re.findall(
            r"with ([0-9]+) successes and ([0-9]+) failures", scraper.last_log
        )[0]
        successes += int(stats[0])
        failures += int(stats[1])
    return (successes, failures)


def scrape(scrapers: list[GigScraper]):
    with ProgBar(len(scrapers)) as bar:
        with ThreadPoolExecutor() as exc:
            threads = [exc.submit(scraper.scrape) for scraper in scrapers]
            while (
                num_complete := len([thread for thread in threads if thread.done()])
            ) < len(scrapers):
                bar.display(prefix=bar.runtime, counter_override=num_complete)
                time.sleep(1)
            bar.display(prefix=bar.runtime, counter_override=len(threads))
    print(f"{len(scrapers)} venues scraped in {bar.timer.elapsed_str}.")
    justification = max(len(scraper.venue.name) for scraper in scrapers) + 1
    print(
        *[
            f"{(scraper.venue.name+':').ljust(justification)} {scraper.last_log[scraper.last_log.rfind('|')+1:]}"
            for scraper in scrapers
        ],
        sep="\n",
    )
    successes, failures = stats(scrapers)
    print(f"Total successes: {successes}")
    print(f"Total failures: {failures}")


def main():
    prescrape_chores()
    try:
        print("Loading scrapers...")
        scrapers = get_scrapers()
        print(f"{len(scrapers)} scrapers loaded.")
        print("Starting scrape...")
        scrape(scrapers)
        print("Scrape finished.")
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
    finally:
        postscrape_chores()
    print("Finished.")
    input("...")


if __name__ == "__main__":
    main()
