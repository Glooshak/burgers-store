from functools import wraps

from .models import Spot


def cache_spot(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            spot = Spot.objects.get(address=args[1])
        except Spot.DoesNotExist:
            if (coordinates := func(*args, **kwargs)) is None:
                return None

            lon, lat = coordinates[0], coordinates[1]
            Spot.objects.create(
                address=args[1],
                lon=lon,
                lat=lat,
            )
        else:
            lon, lat = spot.lon, spot.lat
        return lon, lat

    return wrapper
