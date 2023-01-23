from databased import DataBased


def initialize():
    with DataBased("shows.db") as db:
        db.create_tables(
            [
                "events(date timestamp unique,\
                        venue text,\
                        title text,\
                        acts text,\
                        price text,\
                        eventLink text default null,\
                        actLinks text default null,\
                        info text default null,\
                        dateAdded timestamp,\
                        genres text default null,\
                        inTheFuture int default 1)",
                "venues(name text unique, street text, city text, state text, zip text, website text, calendar_url text, dateAdded timestamp)",
            ]
        )


if __name__ == "__main__":
    with DataBased("shows.db") as db:
        initialize()
