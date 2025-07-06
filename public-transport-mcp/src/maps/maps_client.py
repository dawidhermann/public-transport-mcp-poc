import googlemaps
from typing import Any, NamedTuple


class PlaceGeolocation(NamedTuple):
    lat: float
    lng: float

    def to_dict(self) -> dict[str, float]:
        return {"lat": self.lat, "lng": self.lng}


class MapsClient:
    def __init__(self, api_key: str):
        """
        Initialize the MapsClient with the provided API key.

        :param api_key: Your Google Maps API key.
        """
        self.client: googlemaps.Client = googlemaps.Client(key=api_key)

    def get_geolocation(self, address: str) -> PlaceGeolocation:
        """
        Get directions from origin to destination.

        :param address: Destination.
        :return: Directions as a dictionary.
        """
        result: list[dict[str, Any]] = self.client.geocode(address)
        if not result:
            raise ValueError(f"No geolocation found for address: {address}")
        location = result[0].get("geometry").get("location")
        print(f"Geolocation for address '{address}': {location}")
        return PlaceGeolocation(
            lat=float(location.get("lat")), lng=float(location.get("lng"))
        )
