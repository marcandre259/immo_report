import itertools
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

from src.functions.listing_request import request_parse_listing

MAX_WORKERS = 20

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

status_code = 200
page = 1
max_page = 400

with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [
        executor.submit(request_parse_listing, page, tp, transaction_tp)
        for page, tp, transaction_tp in itertools.product(
            range(1, max_page + 1), ("house", "apartment"), ("for-sale", "for-rent")
        )
    ]

# Correct
results = [future.result() for future in futures]
