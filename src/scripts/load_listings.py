import os
from pathlib import Path
import duckdb
import json
import sys
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
    conn = duckdb.connect(str(SQL()._database))
    sql_create = """
    CREATE TABLE immo_data.listings AS 
    SELECT lpl.id, lpl.property, lpl.transaction
    FROM listing_pl lpl
    """

    conn.execute(sql_create)

    conn.commit()
    conn.close()

else:
    conn = duckdb.connect(str(SQL()._database))

    sql_insert = """
        WITH new_listings AS (
            SELECT lpl.id, lpl.property, lpl.transaction
            FROM listing_pl lpl
            LEFT JOIN immo_data.listings lis ON lpl.id = lis.id
            WHERE lis.id is NULL 
        )
        INSERT INTO immo_data.listings
        SELECT *
        FROM new_listings; 
        """

    conn.execute(sql_insert)

    conn.commit()

    conn.close()


print()

# Clean up and export to a clean listing table
