import datetime

import gruel

import get_to_the_gig.squarespace


def test__SquarespaceCalendar__get_events_by_month_endpoint():
    calendar = get_to_the_gig.squarespace.SquarespaceCalendar(
        gruel.models.Url("https://somevenue.com"), "1234"
    )
    assert calendar.get_events_by_month_endpoint(
        datetime.datetime(2024, 7, 15)
    ) == gruel.models.Url(
        "https://somevenue.com/api/open/GetItemsByMonth?month=07-2024&collectionId=1234"
    )
    print(calendar.get_events_by_month_endpoint(datetime.datetime(2024, 7, 15)))
