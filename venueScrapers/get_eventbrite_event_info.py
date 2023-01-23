import json
from datetime import datetime
from string import ascii_lowercase

import requests
from bs4 import BeautifulSoup


def get_event_info(url: str = None, source: str = None) -> dict:
    if url:
        source = requests.get(url).text
    soup = BeautifulSoup(source, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if "window.__SERVER_DATA__ = " in script.text:
            info = script.text
            break

    info = json.loads(
        info.strip("\n\t\twindow.__SERVER_DATA__ = ").strip(";\n\t"), strict=False
    )
    event = {
        "location": get_event_location(info),
        "org": get_org(info),
        "name": get_name(info),
        "date": get_date(info),
        "salesEnded": info["event"]["shouldShowSalesEndedMessage"],
        "isProtected": info["event"]["isProtected"],
        "compactCheckout": info["event"]["shouldShowCompactCheckout"],
        "statusToDisplay": info["components"]["conversionBar"]["statusToDisplay"],
        "canReserve": info["components"]["conversionBar"]["shouldDisplayRsvp"],
        "price": info["components"]["conversionBar"]["panelDisplayPrice"],
        "checkoutButton": info["components"]["conversionBar"][
            "shouldShowCheckoutButton"
        ],
        "description": get_description(info),
    }
    return event


def to_camel_case(text: str) -> str:
    text = "".join(ch for ch in text.lower() if ch in ascii_lowercase + " ").split()
    return text[0] + "".join(t.capitalize() for t in text[1:])


def get_event_location(info: dict) -> dict:
    try:
        street, city, state_zip = info["components"]["eventMap"]["venueAddress"].split(
            ","
        )
        state, zip_code = state_zip.split()
    except:
        addy = info["components"]["eventDetails"]["location"]["venueMultilineAddress"]
        street = addy[0]
        city, state_zip = addy[1].split(",")
        state, zip_code = state_zip.split()
    return {
        k: v.strip()
        for k, v in {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code,
        }.items()
    }


def get_org(info: dict) -> str:
    try:
        return info["organizer"]["name"]
    except:
        return None


def get_name(info: dict) -> str:
    return info["event"]["name"]


def get_date(info: dict) -> datetime | None:
    try:
        return datetime.strptime(info["event"]["start"]["local"], "%Y-%m-%dT%H:%M:%S")
    except:
        return None


def get_description(info: dict) -> str:
    try:
        description = info["components"]["eventDescription"]["structuredContent"][
            "modules"
        ][0]["text"]
        for ch in ["<P>", "</P>", "amp;", "\\"]:
            description = description.replace(ch, "")
        return description
    except:
        return ""
