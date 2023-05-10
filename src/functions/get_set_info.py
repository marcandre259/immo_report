import json
import re
from typing import Union

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from pathlib import Path

import time

BASE_HTML = "https://www.immoweb.be/en/classified/{0}/{1}/{2}/{3}/{4}"

PROJECT_ROOT = Path(__file__).parents[2]


def get_immo_house_html(storage_info: dict[Union[str, int]]) -> str:
    return BASE_HTML.format(
        storage_info.get("subtype"),
        storage_info.get("transaction"),
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


def request_parse_classified(storage_dict):
    html_address = get_immo_house_html(storage_dict)

    time.sleep(0.01)
    response = requests.get(html_address)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        json_classified = parse_classified(soup)

        # Get other info from the page (description, etc.)
        title_tag = soup.find("meta", itemprop="name")["content"]
        description_tag = soup.find("meta", itemprop="description")["content"]

        other_dict = {}
        if title_tag:
            other_dict["name"] = title_tag
        if description_tag:
            other_dict["description"] = description_tag

        json_classified["other_defined"] = other_dict

        hash_classified = "".join([str(value)[:10] for value in storage_dict.values()])
        hash_classified = re.sub("_", "", hash_classified)

        timestamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
        with open(
            PROJECT_ROOT
            / f"data/classified/classified_{hash_classified}_{timestamp}.json",
            "w",
        ) as json_file:
            json.dump(json_classified, json_file)


if __name__ == "__main__":
    storage_dict = {
        "id": 10536930,
        "subtype": "house",
        "transaction": "for_sale",
        "postal_code": "6830",
        "location": "Bouillon",
    }
    request_parse_classified(storage_dict)
