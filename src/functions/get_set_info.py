import json
import re
from typing import Union

from bs4 import BeautifulSoup

BASE_HTML = "https://www.immoweb.be/en/classified/{0}/{1}/{2}/{3}/{4}"


def get_immo_house_html(storage_info: dict[Union[str, int]]) -> str:
    return BASE_HTML.format(
        storage_info.get("subtype"),
        storage_info.get("transaction_type"),
        storage_info.get("location"),
        storage_info.get("postal_code"),
        storage_info.get("id"),
    )


def extract_storage_info(
    info_dict: dict[Union[dict, str, int]]
) -> dict[Union[int, str]]:
    storage_info = {}
    storage_info["id"] = info_dict["id"]
    storage_info["subtype"] = info_dict["property"]["subtype"].lower()
    storage_info["transaction"] = info_dict["transaction"]["type"].lower()
    storage_info["postal_code"] = info_dict["property"]["location"]["postalCode"]
    storage_info["location"] = info_dict["property"]["location"]["locality"]

    return storage_info


def parse_storage(soup: BeautifulSoup) -> list[dict]:
    # Find all elements with the desired class name containing housing prices
    house_elements = soup.find_all("iw-search")

    re_pageInfo = re.compile(r":results-storage=\'(\[{.*}\])")
    json_pageInfo = re.search(re_pageInfo, house_elements[0].prettify()).group(1)

    json_pageInfo = json.loads(json_pageInfo)

    return json_pageInfo


def parse_classified(soup: BeautifulSoup) -> dict:
    re_classifiedInfo = re.compile(r"window.dataLayer = (\[ .* \]);")

    soup_pretty = soup.prettify().replace("\n", "")
    soup_pretty = re.sub(" +", " ", soup_pretty)

    json_classifiedInfo = re.search(re_classifiedInfo, soup_pretty).group(1)
    json_classifiedInfo = json.loads(json_classifiedInfo)[0]

    return json_classifiedInfo
