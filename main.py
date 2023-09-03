from typing import List
from GeoPost.GeoPost import GeoPost
from Models.PostOffice import PostOffice
from Scraper.PostScraper import PostScraper
import pickle
import os
import json

config_json_path = 'config.json'
with open(config_json_path, 'r') as config_json_file:
    app_config = json.load(config_json_file)

post_offices: List[PostOffice]

pickle_dir = "File Pickle"
post_offices_pickle_path = pickle_dir + os.path.sep + 'post_offices.pkl'
if os.path.exists(post_offices_pickle_path):
    with open(post_offices_pickle_path, "rb") as post_offices_file:
        post_offices = pickle.load(post_offices_file)
else:

    neighborhood_list_dir = 'Scraper'
    neighborhood_list_path = neighborhood_list_dir + os.path.sep + 'milan_neighborhoods.json'
    with open(neighborhood_list_path, 'r') as milan_neighborhoods:
        post_offices_search_queries = json.load(milan_neighborhoods)

    scraper = PostScraper(timeout=10)
    post_offices = scraper.scrape_post_offices(post_offices_search_queries)
    with open(post_offices_pickle_path, "wb") as post_offices_file:
        pickle.dump(post_offices, post_offices_file)

geo_post_offices_pickle_path = pickle_dir + os.path.sep + 'geo_post_offices.pkl'
if os.path.exists(geo_post_offices_pickle_path):
    with open(geo_post_offices_pickle_path, "rb") as geo_post_offices_file:
        post_offices = pickle.load(geo_post_offices_file)
else:
    geo_API_key = app_config.geocoding_API_key

    geo_post = GeoPost(geo_API_key)
    geo_post.set_post_offices_coordinates(post_offices)
    with open(geo_post_offices_pickle_path, "wb") as geo_post_offices_file:
        pickle.dump(post_offices, geo_post_offices_file)