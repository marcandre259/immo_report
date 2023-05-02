import json
import os
import sys
from pathlib import Path

import duckdb
import polars as pl

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

sys.path.append(str(project_root))

from src.functions.read_sql import SQL

# Load listing jsons in /data
data_root = project_root / "data"

listing_paths = [
    str(data_root / file)
    for file in os.listdir(data_root)
    if file.startswith("listings_")
]

listing_data = []
listing_ids = set()
for listing_path in listing_paths:
    with open(listing_path, "r") as listing_dict:
        listing_dict = json.load(listing_dict)
        [
            (listing_data.append(listing), listing_ids.add(listing["id"]))
            for listing in listing_dict
            if listing["id"] not in listing_ids
        ]

listing_pl = pl.from_records(listing_data)

# Load existing listing table
if not SQL().exists("listings"):
    SQL().execute(
        "initialize_listings_table.sql",
        listing_table="listings",
        listing_input="listing_pl",
    )

else:
    SQL().execute(
        "insert_new_listings.sql", listing_table="listings", listing_input="listing_pl"
    )

# Clean up and export to a clean listing table
print()