from Models.PostOffice import PostOffice
from Scraper.PostScraper import PostScraper
import pickle
import os
import json

with open('Scraper/milan_neighborhoods.json', 'r') as milan_neighborhoods:
  post_offices_search_queries = json.load(milan_neighborhoods)

post_offices = []

if os.path.exists("post_offices.pkl"):
    with open("post_offices.pkl", "rb") as post_offices_file:
        post_offices = pickle.load(post_offices_file)
else:
    scraper = PostScraper(timeout=10)
    post_offices += scraper.scrape_post_offices(post_offices_search_queries)
