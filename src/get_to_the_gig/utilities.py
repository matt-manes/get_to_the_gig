import json
import re
from datetime import datetime, timedelta

from typing_extensions import Any, Callable


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


def load_js_dict(js_text: str) -> dict[Any, Any]:
    """Load a javascript dict string."""
    # Get rid of stuff outside of brackets
    js_text = js_text[js_text.find("{") : js_text.rfind("}") + 1]
    # Convert single quotes to double
    js_text = js_text.replace("'", '"')
    # Remove new lines
    js_text = js_text.replace("\n", "")
    # Enclose key names in double quotes
    # Using the first capture group this way to prevent replacing values that have semi colons
    quoter: Callable[[re.Match[str]], str] = lambda m: f'"{m.group(1)}": "'
    js_text = re.sub(r"([a-zA-Z]+\s?): \"", quoter, js_text)
    return json.loads(js_text)
