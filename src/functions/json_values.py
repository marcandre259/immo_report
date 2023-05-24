# Query values from list of json files
# Primary use is filtering relevant files.
import json
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import List


def select_value(filename: str, path: Path, *args):
    error_flag = False
    # Probably smart to parralelize that chunk
    with open(str(path / filename)) as f:
        data_dict = json.load(f)

    for arg in args:
        try:
            data_dict = data_dict[arg]
        except KeyError:
            error_flag = True
            break

    if not error_flag:
        return data_dict

    else:
        return None


def get_json_values_parallel(file_list: List[str], path: Path, *args, ncores: int = 8):
    with ProcessPoolExecutor(max_workers=ncores) as executor:
        futures = [
            executor.submit(select_value, filename, path, *args)
            for filename in file_list
        ]

    results = [future.result() for future in futures]

    return results


def get_json_values(file_list: List[str], path: Path, *args):
    result = [select_value(filename, path, *args) for filename in file_list]

    return result


if __name__ == "__main__":
    pass
