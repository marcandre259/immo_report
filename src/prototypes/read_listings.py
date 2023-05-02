import os
from pathlib import Path

import duckdb

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

data_root = project_root / "data"

listing_paths = [
    str(data_root / file)
    for file in os.listdir(data_root)
    if file.startswith("listings_")
]

q = f"""
DESCRIBE SELECT *
FROM read_json_auto('{listing_paths[0]}')
"""

duckdb.sql(q).show()

conn = duckdb.connect(data_root / "immo_base.db")
