import os 
from pathlib import Path 

current_file = Path(__file__).resolve()
project_root = current_file.parents[1]

import requests
from bs4 import BeautifulSoup
import json 
import re 



# Define the URL
URL = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance'

# Send a request to fetch the webpage
response = requests.get(URL)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    with open(project_root / 'data/webpage_for_sales.html', 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    # Find all elements with the desired class name containing housing prices
    house_elements = soup.find_all('iw-search')

    re_pageInfo = re.compile(r":results-storage=\'(\[{.*}\])")
    json_pageInfo = re.search(re_pageInfo, house_elements[0].prettify()).group(1)

    with open(project_root / 'data/json_string.txt', 'w', encoding='utf-8') as file:
        file.write(json_pageInfo)
    
    json_pageInfo = json.loads(json_pageInfo)

    # Extract and print house prices
    house_prices = [elem.get_text(strip=True) for elem in house_price_elements]
    for index, price in enumerate(house_prices, start=1):
        print(f"{index}. {price}")
else:
    print("Failed to fetch the webpage.")