from typing import Union

BASE_HTML = "https://www.immoweb.be/en/classified/{0}/{1}/{2}/{3}/{4}"


def get_immo_house_html(storage_info: dict[Union[str, int]]) -> str:
    return BASE_HTML.format(
        storage_info.get("subtype"), storage_info.get("transaction_type"), storage_info.get("location"), storage_info.get("postal_code"), storage_info.get("id")
    )


    
