import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Union

import duckdb
import polars as pl

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

sys.path.append(str(project_root))

from src.functions.flatten_dict import flatten_dict
from src.functions.sql import SQL

pl_listings = SQL().obtain("SELECT * FROM listings")

demo = pl_listings["property"][0]

print(flatten_dict(demo))
