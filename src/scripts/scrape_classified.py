import os
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

import sys

sys.path.append(str(project_root))

import json
import logging
import re
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.functions.get_set_info import extract_storage_info, request_parse_classified
from src.functions.sql import SQL

MAX_WORKERS = 20

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Build a list of "info_dict" from existing data
pl_listings = SQL().obtain("SELECT * FROM listings")
dicts_listing = pl_listings.to_dicts()

logging.log(logging.INFO, "Start parsing storage info")

# with ProcessPoolExecutor(MAX_WORKERS) as executor:
#     futures = [
#         executor.submit(extract_storage_info, dict_listing)
#         for dict_listing in dicts_listing
#     ]

dicts_storage = [extract_storage_info(dict_listing) for dict_listing in dicts_listing]

logging.log(logging.INFO, "Start scraping classified information")

# Routine to parse storage page and save info as json (in a classified folder)
with ProcessPoolExecutor(MAX_WORKERS) as executor:
    futures = [
        executor.submit(request_parse_classified, dict_storage)
        for dict_storage in dicts_storage
    ]

# Correct
empty = [future.result() for future in futures]
