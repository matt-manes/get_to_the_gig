from datetime import datetime
from pathier import Pathier

from databased import DataBased

root = Pathier(__file__).parent

db = DataBased(root / "shows.db")
while True:
    try:
        venues = [venue["name"] for venue in db.get_rows("venues")]
        db.close()
        name = input("Venue name: ")
        if name in venues:
            print(f"{name} already in venues")
        else:
            street = input("Street: ")
            city = input("City: ")
            state = input("State: ")
            zip_code = input("Zip: ")
            website = input("Website: ")
            calendar_url = input("Calendar url: ")
            date_added = datetime.now()
            reference_name = name.replace(" ", "").replace("'", "")
            reference_name = reference_name[0].lower() + reference_name[1:]
            db.add_row(
                "venues",
                (
                    name,
                    street,
                    city,
                    state,
                    zip_code,
                    website,
                    calendar_url,
                    date_added,
                    reference_name,
                ),
            )
            db.close()
            template = (root / "venueScrapers" / "template.py").read_text()
            template = template.replace("$calendar_url", calendar_url)
            (root / "venueScrapers" / f"{reference_name}.py").write_text(template)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
