from datetime import datetime

import lincoln_hall
from bs4 import BeautifulSoup
from gig_scraper import GigScraper
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()

import models


# calendar url: https://lh-st.com
class Venue(lincoln_hall.Venue):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem


if __name__ == "__main__":
    venue = Venue()
    venue.scrape()
    print(venue.last_log)
