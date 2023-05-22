# Query values from list of json files
# Primary use is filtering relevant files. 
from typing import Union, List
import json

def get_json_values(file_list: List[str], path: str, *args):
    value_list = []
    for file in file_list:
        # Probably smart to parralelize that chunk
        with open(path + file) as f:
            data_dict = json.load(f)

        for arg in args:
            try: 
                data_dict = data_dict[arg]
            except Exception as e:
                print(e)
                break 

        value_list.append(data_dict)

    return value_list
        

        
def f(*args):
    pass

if __name__ == "__main__":
    f("a", "b")