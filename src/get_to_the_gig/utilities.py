from datetime import datetime, timedelta


def get_days_away_daterange(days_away: tuple[int, int]) -> tuple[datetime, datetime]:
    """Takes a starting and ending number of days from today and returns the equivalent range as two `datetime` objects."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
        days=days_away[0]
    )
    stop = today.replace(hour=23, minute=59, second=59, microsecond=9999) + timedelta(
        days=days_away[1]
    )
    return (start, stop)
