import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.distance import geodesic

logger = logging.getLogger("GeoAgile.Geocoder")

class LocationService:
    def __init__(self, user_agent="geo_agile_starlink_bot"):
        self.geolocator = Nominatim(user_agent=user_agent)

    def get_address_from_coords(self, lat, lon):
        """
        Reverse geocodes latitude and longitude to an address.
        """
        try:
            logger.info(f"Geocoding coordinates: {lat}, {lon}")
            location = self.geolocator.reverse((lat, lon), exactly_one=True, language='en')
            
            if location:
                logger.info(f"Found address: {location.address}")
                return location.address
            else:
                logger.warning("No address found for these coordinates.")
                return None

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected geocoding error: {e}")
            return None

    def calculate_distance_km(self, coord1, coord2):
        """
        Calculates distance in km between two (lat, lon) tuples.
        """
        try:
            return geodesic(coord1, coord2).kilometers
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return 0.0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    service = LocationService()
    # Test with Eiffel Tower coordinates
    addr = service.get_address_from_coords(48.8584, 2.2945)
    print(f"Address: {addr}")
