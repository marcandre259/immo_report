import os
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parents[1]

import sys

sys.path.append(str(project_root))

import requests
from bs4 import BeautifulSoup
import json
import re

from src.functions.get_set_info import (
    get_immo_house_html,
    extract_storage_info,
    parse_storage,
    parse_classified,
)

# Define the URL
URL = "https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance"

# Send a request to fetch the webpage
response = requests.get(URL)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    json_listings = parse_storage(soup)

    storage_info = extract_storage_info(json_listings[0])

    house_url = get_immo_house_html(storage_info)

    response = requests.get(house_url)

    soup = BeautifulSoup(response.content, "html.parser")

    classified_dict = parse_classified(soup)
