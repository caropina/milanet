from typing import List
import requests
from Models.PostOffice import PostOffice


class GeoPost:

    """
        GeoPost constructor.

        Input:
            - API_key: Google's geocoding API key

        Initializes:
            - API_key: Google's geocoding API key
            - geo_url: Google's geocoding API url
    """
    def __init__(self, API_key: str):
        self.API_key = API_key
        self.geo_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    """
        Executes a request to Google's Geocoding API to get latitude and longitude for a post office.
        
        Input:
            - post_office: the post office to update
            
        Returns:
            - post_office object with filled in coordinates, if the request succeeds
    """
    def set_post_office_coordinates(self, post_office: PostOffice):
        param = {
            'key': self.API_key,
            'address': post_office.indirizzo + ', Milano'
        }

        response = requests.get(self.geo_url, params=param).json()

        if response['status'] == 'OK':
            coordinate = response['results'][0]['geometry']
            lat = coordinate['location']['lat']
            lon = coordinate['location']['lng']
            post_office.coordinate = {'latitudine': lat, 'longitudine': lon}

        else:
            raise (Exception("Coordinates not found for " + post_office.indirizzo + ' Milano'))

        return post_office

    """
        Executes a request to Google's Geocoding API to get latitude and longitude for a list of post offices.

        Input:
            - post_offices: the list of post offices to update
            
        Returns:
            - post_offices list with filled in coordinates, if the requests succeeds
    """

    def set_post_offices_coordinates(self, post_offices: List[PostOffice]):

        for post_office in post_offices:
            try:
                self.set_post_office_coordinates(post_office)
            except Exception as err:
                print(err)

        return post_offices
