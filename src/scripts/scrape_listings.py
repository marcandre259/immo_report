import os
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

import sys

sys.path.append(str(project_root))

import json
import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.functions.listing_request import request_parse_listing
from concurrent.futures import ProcessPoolExecutor


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

status_code = 200
page = 1
max_page = 400


with ProcessPoolExecutor(max_workers=16) as executor:
    futures = [
        executor.submit(request_parse_listing, page) for page in range(1, max_page + 1)
    ]

results = [future.result() for future in futures]
