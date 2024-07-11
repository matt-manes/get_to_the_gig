import lincoln_hall
from pathier import Pathier

root = Pathier(__file__).parent
(root.parent).add_to_PATH()


# calendar url: https://lh-st.com
class VenueScraper(lincoln_hall.VenueScraper):
    @property
    def name(self) -> str:
        return Pathier(__file__).stem


if __name__ == "__main__":
    venue = VenueScraper()
    venue.scrape()
    print(venue.last_log)
