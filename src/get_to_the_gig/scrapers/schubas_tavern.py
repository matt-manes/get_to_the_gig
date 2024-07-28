# type: ignore
import lincoln_hall


# calendar url: https://lh-st.com
class EventParser(lincoln_hall.EventParser): ...


class VenueScraper(lincoln_hall.VenueScraper): ...


if __name__ == "__main__":
    venue = VenueScraper()
    venue.show_parse_items_prog_bar = True
    # venue.test_mode = True
    venue.scrape()
    print(f"{venue.success_count=}")
    print(f"{venue.fail_count=}")
