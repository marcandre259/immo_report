import os
from pathlib import Path
import duckdb
import json

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

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

# Load existing listing table

# Find listings not yet in table and insert

# Clean up and export to a clean listing table
