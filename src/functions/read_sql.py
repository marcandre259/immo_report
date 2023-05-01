from pathlib import Path
import os
from typing import List, Optional
from threading import Thread
import duckdb
import polars as pl

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
SQL_PATH = project_root / "src/sql"
DATABASE = project_root / "data/immo_data.db"


class SQL:
    def __init__(self):
        self._sql_path = SQL_PATH
        self._database = DATABASE

    def _read_sql(self, file_name: str) -> List[str]:
        file_path = self._sql_path / file_name
        with open(file_path, "r") as sql_queries:
            query_list = sql_queries.read().split(";")

        return query_list

    def execute(self, file_name: str) -> None:
        conn = duckdb.connect(str(self._database))
        queries = self._read_sql(file_name)

        for query in queries:
            conn.execute(query)

        conn.commit()

    def obtain(self, query_name: Optional[str] = None, file_name: Optional[str] = None):
        conn = duckdb.connect(str(self._database))

        if isinstance(query_name, str):
            return conn.sql(query_name).pl()

        elif isinstance(file_name, str):
            query = self._read_sql(file_name)[0]
            return conn.sql(query).pl()


if __name__ == "__main__":
    output = SQL().obtain(file_name="bland_query.sql")

    print(output)
