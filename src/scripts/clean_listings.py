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

cleaned_table_name = "cleaned_listings"

logging.info("Loading listings and cleaning")
pl_listings = SQL().obtain("SELECT * FROM listings")

cleaned_listings = []
for d in pl_listings.to_dicts():
    cleaned_d = flatten_dict(d)
    cleaned_listings.append(cleaned_d)

pl_cleaned = pl.from_records(cleaned_listings)

logging.info(f"Inserting the cleaned listings into {cleaned_table_name}")
if SQL().exists(cleaned_table_name):
    SQL().drop_table(cleaned_table_name)

# Insert the cleaned table
SQL().execute(
    "insert_cleaned_listings.sql",
    cleaned_listings_name=cleaned_table_name,
    pl_cleaned="pl_cleaned",
)
