import json
import logging
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.functions.get_set_info import extract_storage_info, parse_storage

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

import sys

sys.path.append(str(project_root))


def request_parse_listing(page: int, type: str, transaction: str):
    # Define the URL
    URL = f"https://www.immoweb.be/en/search/{type}/{transaction}?countries=BE&page={page}&orderBy=relevance"

    # Send a request to fetch the webpage
    time.sleep(0.1)
    response = requests.get(URL)

    status_code = response.status_code

    # Check if the request was successful (status code 200)
    if status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        json_listings = parse_storage(soup)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(
            project_root
            / f"data/listings/listings_{page}_{type}_{transaction}_{timestamp}.json",
            "w",
        ) as json_file:
            json.dump(json_listings, json_file)

        ## Example of storage info extraction (for deeper query)
        storage_info = extract_storage_info(json_listings[0])

        logging.info(msg=f"Succeeding in extracting listings at page {page}")

    else:
        logging.info(msg=f"Failed in extracting listings at page {page}")

    return "Boop"
