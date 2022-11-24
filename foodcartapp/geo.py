from typing import Optional

import requests
from geopy import distance

from distances.utils import cache_spot


@cache_spot
def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def calculate_distance(a: Optional[tuple[float, float]], b: Optional[tuple[float, float]]) -> float:
    # If Yandex is not able to determine the distance of any destination
    # we cast -1
    return round(
        distance.distance(a, b).km,
        2,
    ) if all([a, b]) else -1
