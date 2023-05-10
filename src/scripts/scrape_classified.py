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

from src.functions.sql import SQL
from src.functions.get_set_info import (
    get_immo_house_html,
    extract_storage_info,
    parse_storage,
)

MAX_WORKERS = 16

# Build a list of "info_dict" from existing data
pl_listings = SQL().obtain("SELECT * FROM listings")
dicts_listing = pl_listings.to_dicts()

with ProcessPoolExecutor(MAX_WORKERS) as executor:
    futures = [
        executor.submit(extract_storage_info, dict_listing)
        for dict_listing in dicts_listing
    ]

dicts_storage = [future.result() for future in futures]

# Extract storage info from these info dict
print()

# Routine to parse storage page and save info as json (in a classified folder)
