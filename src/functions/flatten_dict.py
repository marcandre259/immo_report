from typing import Dict, Union


def flatten_dict(details: Dict[str, Union[str, Dict]]) -> Dict[str, str]:
    flat_dict = {}

    def flatten_level(level: Dict[str, Union[str, Dict]], prefix=""):
        for key, value in level.items():
            if isinstance(value, dict):
                prefix += f"{key}_"
                flatten_level(value, prefix)
            else:
                key = f"{prefix}{key}"
                flat_dict[key] = value

    flatten_level(details)

    return flat_dict
