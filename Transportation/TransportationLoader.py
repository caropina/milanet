import os
import pickle
from typing import List
import requests
from Transportation.Graph import Graph
from Transportation.Models.TransportationStop import TransportationStop


class TransportationLoader:
    """
        TransportationLoader constructor.

        Initializes:
        - the graph structure used to represent the transportation network

    """
    def __init__(self):
        self.graph = Graph()

    """
        Converts a JSON list into a list of objects of type TransportationStop.
    
        Input:
            - transportation_json_list: a JSON list storing all public transportation stops in sequence.
    
        Returns:
            - A list of TransportationStop objects, containing the same information as the original JSON.
    """
    def __convert_transportation_json_list_to_object_list(self, transportation_json_list: []) -> List[TransportationStop]:
        transportation_stop_list: List[TransportationStop] = []
        for i in range(len(transportation_json_list)):
            transportation_stop = TransportationStop()
            transportation_stop.ubicazione = transportation_json_list[i]['ubicazione']
            transportation_stop.mezzo = transportation_json_list[i]['mezzo']
            transportation_stop.percorso = int(transportation_json_list[i]['percorso'])
            transportation_stop.num = int(transportation_json_list[i]['num'])
            transportation_stop.long = transportation_json_list[i]['LONG_X_4326']
            transportation_stop.lat = transportation_json_list[i]['LAT_Y_4326']
            transportation_stop.id_ferm = int(transportation_json_list[i]['id_ferm'])
            transportation_stop.linea = transportation_json_list[i]['linea']

            transportation_stop_list.append(transportation_stop)

        return transportation_stop_list
    def __request_metro_transportation_path_stops(self, paths) -> []:
        records = []
        for i in paths:
            p = i['percorso']
            url = f"https://dati.comune.milano.it/api/3/action/datastore_search_sql?sql=SELECT *, fermate.nome as ubicazione from \"0555a0ae-9493-46ca-bc3d-65544f4e99b2\" as composizioni JOIN \"0f4d4d05-b379-45a4-9a10-412a34708484\" as fermate ON composizioni.id_ferm = fermate.id_amat JOIN \"f3ce3f16-0e13-4136-bbe1-d1b37b612f6f\" as linee on composizioni.percorso = linee.percorso WHERE composizioni.percorso = {p} ORDER BY composizioni.num"
            response = requests.get(url)
            response_stops_json = response.json()
            records += response_stops_json['result']['records']

        return records

    """
        Requests and retrieves information about metro transportation stops for a given list of paths.

        Input:
            - paths: a list of metro transportation paths.

        Returns:
            - a list of records containing information about metro transportation stops.
    """
    def __request_metro_transportation_path(self):
        url = "https://dati.comune.milano.it/api/3/action/datastore_search_sql?sql=SELECT DISTINCT percorso from \"0555a0ae-9493-46ca-bc3d-65544f4e99b2\" as composizioni"
        response = requests.get(url)
        response_routes_stops_json = response.json()
        return response_routes_stops_json['result']['records']

    """
    Loads metro transportation data from a pickle file or fetches and processes it if the file doesn't exist.

    Returns:
        - A list of metro transportation data objects.
    """
    def __load_metro_transportation(self):
        metro_transportation_list_path = 'Pickles' + os.path.sep + 'metro_transportation.pkl'

        if os.path.exists(metro_transportation_list_path):
            with open(metro_transportation_list_path, 'rb') as metro_transportation_list_file:
                metro_transportation_list = pickle.load(metro_transportation_list_file)

        else:
            paths = self.__request_metro_transportation_path()
            metro_transportation_list = self.__request_metro_transportation_path_stops(paths)

            with open(metro_transportation_list_path, 'wb') as metro_transportation_list_file:
                metro_transportation_list = self.__convert_transportation_json_list_to_object_list(metro_transportation_list)
                pickle.dump(metro_transportation_list, metro_transportation_list_file)

        return metro_transportation_list

    """
    Requests and retrieves information about surface transportation stops for a given list of paths.

    Input:
        - paths: a list of transportation paths.

    Returns:
        - a list of records containing information about surface transportation stops.
    """
    def __request_surface_transportation_path_stops(self, paths):
        records = []
        for i in paths:
            p = i['percorso']
            url = f"https://dati.comune.milano.it/api/3/action/datastore_search_sql?sql=SELECT * from \"d4530625-dd71-4e8c-8eb4-bf4e26f2500e\" as composizioni JOIN \"2a52d51d-66fe-480b-a101-983aa2f6cbc3\" as fermate ON composizioni.id_ferm = fermate.id_amat JOIN \"d4408a03-ef86-40df-a4a9-e738d05e03e4\" as linee on composizioni.percorso = linee.percorso WHERE composizioni.percorso = {p} ORDER BY composizioni.num"
            response = requests.get(url)
            response_stops_json = response.json()
            records += response_stops_json['result']['records']

        return records

    """
        Requests and retrieves distinct surface transportation paths.

        Returns:
            - A list of distinct surface transportation paths.
    """
    def __request_surface_transportation_path(self):
        url = "https://dati.comune.milano.it/api/3/action/datastore_search_sql?sql=SELECT DISTINCT percorso from \"d4530625-dd71-4e8c-8eb4-bf4e26f2500e\" as composizioni"
        response = requests.get(url)
        response_routes_stops_json = response.json()
        return response_routes_stops_json['result']['records']

    """
       Loads surface transportation data from a pickle file or fetches and processes it if the file doesn't exist.

       Returns:
           - A list of surface transportation data objects.
    """
    def __load_surface_transportation(self):

        surface_transportation_list_path = 'Pickles' + os.path.sep + 'surface_transportation.pkl'

        if os.path.exists(surface_transportation_list_path):
            with open(surface_transportation_list_path, 'rb') as surface_transportation_list_file:
                surface_transportation_list = pickle.load(surface_transportation_list_file)

        else:
            paths = self.__request_surface_transportation_path()
            surface_transportation_list = self.__request_surface_transportation_path_stops(paths)

            with open(surface_transportation_list_path, 'wb') as surface_transportation_list_file:
                surface_transportation_list = self.__convert_transportation_json_list_to_object_list(surface_transportation_list)
                pickle.dump(surface_transportation_list, surface_transportation_list_file)

        return surface_transportation_list

    """
        Converts a list of TransportationStop objects into a graph representation.
        
        Input:
            - transportation_list: A list of TransportationStop objects.
        
        Returns:
            - A graph representation of the transportation network.
    """
    def __convert_transportation_to_graph(self, transportation_list: List[TransportationStop]) -> Graph:
        paths = {}
        for transportation in transportation_list:
            if transportation.percorso not in paths:
                paths[transportation.percorso] = [transportation]
            else:
                paths[transportation.percorso].append(transportation)

        for key in paths:
            paths[key].sort(key=lambda x: x.num)

            prev_node = None
            for transportation in paths[key]:
                if prev_node == None:
                    self.graph.add_vertex(transportation)
                else:
                    self.graph.add_vertex(transportation)
                    self.graph.add_edge([prev_node, transportation])
                prev_node = transportation

    """
        Loads transportation data, combines metro and surface transportation data, and converts it into a graph representation of the transportation network.

        Returns:
            - A graph representation of the transportation network.
     """
    def load_transportation_as_graph(self) -> Graph:
        transportation_list = []
        transportation_list += self.__load_metro_transportation()
        transportation_list += self.__load_surface_transportation()

        return self.__convert_transportation_to_graph(transportation_list)