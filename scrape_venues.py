import argparse
import importlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from databased import DataBased
from gitbetter import Git
from noiftimer import Timer
from printbuddies import ProgBar

from clear_old_events import clear_old_events

root = Path(__file__).parent


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=10,
        help=""" The number of simultaneous scrapers to run.
        Pick a lower number if your machine has a low core count or low ram.""",
    )

    args = parser.parse_args()

    return args


def update_consecutive_crash_tracker(scrape_results: dict):
    trackerpath = root / "crash_tracker.json"
    if not trackerpath.exists():
        trackerpath.write_text("{}")
    crash_tracker = json.loads((root / "crash_tracker.json").read_text())
    for result in scrape_results:
        # if scraper name isn't present or the scrape was succesfull, set to 0
        if result not in crash_tracker or scrape_results[result]:
            crash_tracker[result] = 0
        else:
            crash_tracker[result] += 1
    (root / "crash_tracker.json").write_text(json.dumps(crash_tracker, indent=2))


def run_scrapers():
    start_time = datetime.today()
    scrapers_dir = root / "venueScrapers"
    sys.path.insert(0, str(scrapers_dir))
    # reference_name column is how the scraper files are named.
    with DataBased("shows.db") as db:
        scraper_files = [
            (scrapers_dir / name[0]).with_suffix(".py")
            for name in db.get_rows(
                "venues", columns_to_return=["reference_name"], values_only=True
            )
        ]

    scrapers = [
        importlib.import_module(str(scraper.stem)).Scraper()
        for scraper in scraper_files
        if "# not_ready" not in scraper.read_text()
    ]
    bar = ProgBar(len(scrapers))
    timer = Timer()
    with ThreadPoolExecutor(args.threads) as executor:
        print(f"beginning scrape with {args.threads} threads")
        timer.start()
        scrapers_to_run = [executor.submit(scraper.scrape) for scraper in scrapers]
        while any(scraper.running() for scraper in scrapers_to_run):
            num_complete = len(
                [scraper for scraper in scrapers_to_run if scraper.done()]
            )
            bar.display(
                prefix=f"elapsed time: {timer.elapsed_str}",
                counter_override=num_complete,
            )
            time.sleep(1)
        num_complete = len([scraper for scraper in scrapers_to_run if scraper.done()])
        bar.display(
            prefix=f"{num_complete=} elapsed time: {timer.elapsed_str}",
            counter_override=num_complete,
        )
        print()
        print("all done")
        end_time = datetime.today()
        deets = {
            "startTime": str(start_time),
            "endTime": str(end_time),
            "elapsedTime": timer.elapsed_str,
        }
        results = {
            scraper.scraper_path.stem: scraper.scrape_successful for scraper in scrapers
        }
        results = {k: results[k] for k in sorted(results.keys())}
        deets |= results
        (root / "scrapeReport.json").write_text(json.dumps(deets, indent=2))
        update_consecutive_crash_tracker(results)
        print(json.dumps(deets, indent=2))
    print("Committing and syncing shows.db to Github...")
    git = Git()
    git.commit_files(["shows.db"], "chore: push shows.db update")
    git.push()
    print("Sync complete.")
    input("...")


if __name__ == "__main__":
    args = get_args()
    clear_old_events()
    run_scrapers()
    try:
        ...
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
