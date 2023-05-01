import os
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

import sys

sys.path.append(str(project_root))

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

from src.functions.get_set_info import extract_storage_info, parse_storage

# Define the URL
URL = "https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance"

# Send a request to fetch the webpage
response = requests.get(URL)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    json_listings = parse_storage(soup)

    timestamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
    with open(project_root / f"data/listings_{timestamp}.json", "w") as json_file:
        json.dump(json_listings, json_file)

    ## Example of storage info extraction (for deeper query)
    storage_info = extract_storage_info(json_listings[0])
