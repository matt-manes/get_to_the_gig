from databased import DataBased


def initialize():
    with DataBased("shows.db") as db:
        db.create_tables(
            [
                "events(date timestamp,\
                        venue text,\
                        title text,\
                        acts text,\
                        price text,\
                        event_link text default null,\
                        act_links text default null,\
                        info text default null,\
                        date_added timestamp,\
                        genres text default null,\
                        in_the_future int default 1)",
                "venues(name text unique, street text, city text, state text, zip text, website text, calendar_url text, date_added timestamp)",
            ]
        )


if __name__ == "__main__":
    with DataBased("shows.db") as db:
        db.drop_table("events")

    initialize()
