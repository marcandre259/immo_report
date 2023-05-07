import os
from pathlib import Path
from threading import Thread
from typing import List, Optional

import duckdb
import polars as pl

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

DATABASE = project_root / "data/immo_data.db"
SQL_PATH = project_root / "src/sql"


class SQL:
    def __init__(self):
        self._sql_path = SQL_PATH
        self._database = DATABASE

    def _read_sql(self, file_name: str, **kwargs) -> List[str]:
        file_path = self._sql_path / file_name
        with open(file_path, "r") as sql_query:
            query = sql_query.read().split(";")[0]

        query = query.format(**kwargs)

        return query

    def execute(self, file_name: str, **kwargs) -> None:
        conn = duckdb.connect(str(self._database))
        query = self._read_sql(file_name, **kwargs)

        conn.execute(query)

        conn.commit()

    def obtain(
        self,
        query_name: Optional[str] = None,
        file_name: Optional[str] = None,
        **kwargs,
    ):
        conn = duckdb.connect(str(self._database))

        if isinstance(query_name, str):
            return conn.sql(query_name, **kwargs).pl()

        elif isinstance(file_name, str):
            query = self._read_sql(file_name, **kwargs)
            return conn.sql(query).pl()

    def exists(self, table_name: str) -> bool:
        conn = duckdb.connect(str(self._database))

        try:
            output = conn.sql(f"SELECT * FROM {table_name} LIMIT 5;").fetchone()
            return True
        except (duckdb.CatalogException, duckdb.InvalidInputException):
            return False

    def drop_table(self, table_name: str):
        conn = duckdb.connect(str(self._database))

        try:
            output = conn.sql(f"DROP TABLE {table_name};")
        except duckdb.CatalogException as err:
            print(err)


if __name__ == "__main__":
    output = SQL().drop_table("blooomba")

    output = SQL().obtain(file_name="bland_query.sql")

    print(output)

    output = SQL().exists("boomba_ja")

    print(output)

    # Try out argument input capability
    SQL()._read_sql(
        "initialize_listings_table.sql",
        listing_table="listings",
        listing_input="blank_pl",
    )
