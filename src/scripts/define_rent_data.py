import json
from datetime import datetime
import os
from pathlib import Path
import logging
import re
import sys

import pandas as pd
import polars as pl
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import plotly.express as px

import statsmodels.api as sm

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

ROOT_PATH = Path(os.path.abspath(""))

sys.path.append(str(ROOT_PATH))
from src.functions.json_values import (
    get_json_values,
)
from src.functions.flatten_dict import flatten_dict

CLASSIFIED_PATH = ROOT_PATH / "data/classified"
SCRAPING_DAY = 22

logging.log(
    logging.INFO, "Start scraping classified data from {}".format(CLASSIFIED_PATH)
)


# Extract date of classified
def get_day(file_name: str):
    ymd_groups = r"^classified_.+_(\d+)_(\d+).json$"
    year_string = re.findall(ymd_groups, file_name)[0][
        0
    ]  # First element of list, first group
    return datetime.strptime(year_string, "%Y%m%d").day


# Keep classified files that were captured on the 15th of May
list_filenames = os.listdir(CLASSIFIED_PATH)
new_list_filenames = []

for filename in list_filenames:
    try:
        filename_day = get_day(filename)
    except IndexError:
        print(
            filename
        )  # Some filenames are changed by mistakes <- shouldn't happen too often
        continue
    if filename_day == SCRAPING_DAY:
        new_list_filenames.append(filename)

list_filenames = new_list_filenames

# Find and select renting locations
list_transactions = get_json_values(
    list_filenames, CLASSIFIED_PATH, "classified", "transactionType"
)

## Filter for rent and apartments
list_types = get_json_values(list_filenames, CLASSIFIED_PATH, "classified", "type")

## Filter JSONS about apartment to rent
bl_type = np.isin(np.array(list_types), ["apartment", "apartment group"])
bl_transact = np.isin(np.array(list_transactions), "for rent")
bl = np.logical_and(bl_type, bl_transact)

logging.log(logging.INFO, "Get relevant locations and parse json data into dataframe")

list_apartrent = [filename for filename, b in zip(list_filenames, bl) if b]


# Defining component I want to extract from the apartments to rent
component_dict = {
    "listing_id": ["classified", "id"],
    "price": ["classified", "price"],
    "contact_type": ["customer", "family"],
    "contact_name": ["customer", "name"],
    "subtype": ["classified", "subtype"],
    "zip_code": ["classified", "zip"],
    "construction_year": ["building", "constructionYear"],
    "building_condition": ["building", "condition"],
    "energy_consumption": ["certificates", "primaryEnergyConsumptionLevel"],
    "energy_class": ["classified_table", "energy_class"],
    "n_bedrooms": ["bedroom", "count"],
    "land_surface": ["land", "surface"],
    "surroundings_type": ["classified_table", "surroundings_type"],
    "living_area": ["classified_table", "living_area"],
}

pl_apart = pl.DataFrame()

for key in component_dict.keys():
    data_arr = get_json_values(list_apartrent, CLASSIFIED_PATH, *component_dict[key])
    pl_apart = pl_apart.with_columns(pl.lit(data_arr).alias(key))

logging.log(logging.INFO, "Correct prices so always float, always upper of range")

# With price, save only max price, parse
price_list = pl_apart.select("price").to_numpy().ravel().tolist()

adjusted_prices = []

pattern = r"(\d+)( - )?(\d+)"
for price in price_list:
    found = re.findall(pattern, price)
    try:
        if found[0][1] != "":
            adjusted_prices.append(found[0][2])
        else:
            adjusted_prices.append(price)
    except IndexError:
        adjusted_prices.append(None)

# Replace adjusted prices (we retain the max rent price)
pl_apart = pl_apart.with_columns(pl.lit(adjusted_prices).cast(pl.Int64).alias("price"))

# Cast rows as relevant
q = [
    pl.col("price").cast(pl.Int64),
    pl.col("n_bedrooms").cast(pl.Int64),
    pl.col("energy_consumption").cast(pl.Int64),
    pl.col("construction_year").cast(pl.Int64),
    pl.col("zip_code").cast(pl.Int64),
    pl.col("living_area").cast(pl.Float64),
]

pl_apart = pl_apart.with_columns(q)

# Contact types
pl_apart.groupby("contact_type").count()


logging.log(logging.INFO, "Load geo data")
# Load zipcodes and coordinates data (and merge)
pl_zip = pl.read_csv(ROOT_PATH / "data/zipcode-belgium.csv", has_header=False)
pl_zip.columns = ["zip_code", "commune", "geo_long", "geo_lat"]

pl_apart = pl_apart.join(pl_zip, on="zip_code", how="left")

# Check for duplicate ids -> A lot
# Filter them out
q = pl.col("listing_id").is_duplicated().is_not()
pl_apart = pl_apart.filter(q)

# Read municipality shape file
gpd_municipalities = gpd.read_file(
    ROOT_PATH / "data/adminvector_3812.gpkg", layer="municipality"
)

# Convert to pandas
df_apart = pl_apart.to_pandas()

# Spatial join
apart_geom = [Point(x, y) for x, y in zip(df_apart["geo_long"], df_apart["geo_lat"])]
df_apart = df_apart.drop(["geo_long", "geo_lat"], axis=1)
gpd_apart = gpd.GeoDataFrame(df_apart, geometry=apart_geom)

gpd_municipalities = gpd_municipalities.to_crs("EPSG:4326")

gpd_apart = gpd_apart.sjoin(gpd_municipalities, how="left", predicate="within")

logging.log(logging.INFO, "Compute relevant pricing info")

# Get rent price per m2
gpd_apart["price_m2"] = np.round(gpd_apart["price"] / gpd_apart["living_area"], 2)

# I want the median and the deviation from the median (of a municipality)
gpd_apart["median_price_m2"] = gpd_apart.groupby("namedut")["price_m2"].transform(
    "median"
)
gpd_apart["deviation_price_m2"] = gpd_apart["price_m2"] - gpd_apart["median_price_m2"]

gpd_apart = gpd_apart.loc[gpd_apart["listing_id"] != "10370135", :]

# Mode city per contact name
gpd_contact = (
    gpd_apart.groupby(["contact_name", "namedut"])["namedut"]
    .count()
    .rename("count_city")
    .reset_index()
)

gpd_contact["max_count_city"] = gpd_contact.groupby("contact_name")[
    "count_city"
].transform("max")
gpd_contact = gpd_contact.loc[
    gpd_contact["count_city"] == gpd_contact["max_count_city"], :
].drop(["count_city", "max_count_city"], axis=1)
gpd_contact = gpd_contact.rename({"namedut": "contact_city_mode"}, axis=1)

gpd_apart = pd.merge(gpd_apart, gpd_contact, on="contact_name", how="left")

# Ratio deviation from median (also important to compare cities)
gpd_apart["ratio_deviation_price_m2"] = np.round(
    gpd_apart["price_m2"] / gpd_apart["median_price_m2"], 2
)

logging.log(logging.INFO, "Writing apartment data into {}".format(ROOT_PATH))
gpd_apart.to_parquet(ROOT_PATH / "data/apart_df.parquet")

logging.log(logging.INFO, "Writing municipality data into {}".format(ROOT_PATH))
gpd_municipalities.to_file(ROOT_PATH / "data/municipalities_geo.gpkg")
