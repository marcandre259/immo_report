# Query values from list of json files
# Primary use is filtering relevant files.
import json
from pathlib import Path
from typing import List


def get_json_values(file_list: List[str], path: Path, *args):
    value_list = []
    for file in file_list:
        error_flag = False
        # Probably smart to parralelize that chunk
        with open(str(path / file)) as f:
            data_dict = json.load(f)

        for arg in args:
            try:
                data_dict = data_dict[arg]
            except KeyError:
                error_flag = True
                break

        if not error_flag:
            value_list.append(data_dict)

    return value_list


if __name__ == "__main__":
    pass
