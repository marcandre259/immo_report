import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

import warnings

import pandas as pd
import geopandas as gpd
from pandas.errors import SettingWithCopyWarning
import numpy as np

import os
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parents[2]

import sys

sys.path.append(str(project_root))

## Declare app
app = dash.Dash(__name__)

## Prepare data

## Load predictions
df_imp = pd.read_parquet(project_root / "data/pm2_df.parquet")

## Load actual
df_actual = pd.read_parquet(project_root / "data/apart_df.parquet")

gdf_municipalities = gpd.read_file(project_root / "data/municipalities_geo.gpkg")
gdf_municipalities = gdf_municipalities[["tgid", "namedut", "geometry"]]

municipality_names = list(np.sort(df_actual["namedut"].unique()))

max_living_area = int(df_actual["living_area"].max() // 1000 * 2000)
min_living_area = int(df_actual["living_area"].min() // 10 * 10)

## layout
app.layout = html.Div(
    [
        html.Div(
            [
                # Filters
                html.Div(
                    [
                        html.H3("Filters"),
                        dcc.Dropdown(
                            id="municipality-dropdown",
                            value="Leuven",
                            options=municipality_names,  # To be filled with the municipalities data
                            placeholder="Select a Municipality",
                        ),
                        html.Div(
                            [
                                html.Label("Living Area Range (m2):"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="min-living-area-input",
                                            type="number",
                                            value=min_living_area,
                                            min=min_living_area,
                                            max=max_living_area,
                                            step=5,
                                            placeholder="Min Living Area",
                                        ),
                                        dcc.Input(
                                            id="max-living-area-input",
                                            type="number",
                                            value=max_living_area,
                                            min=min_living_area,
                                            max=max_living_area,
                                            step=5,
                                            placeholder="Max Living Area",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "space-between",
                                    },
                                ),
                            ]
                        ),
                    ],
                    className="menu",
                ),
                html.Div(id="expected-price-per-month"),
                # User Input for Living Area and Price
                html.Div(
                    [
                        html.H3("Your info"),
                        html.Label("Your Living Area (m2):"),
                        dcc.Input(
                            id="user-living-area-input",
                            type="number",
                            min=10,
                            max=2000,
                            step=1,
                            placeholder="Your Living Area",
                        ),
                        html.Label("Your Price per Month (€):"),
                        dcc.Input(
                            id="user-price-input",
                            type="number",
                            min=1,
                            step=1,
                            placeholder="Your Price",
                        ),
                        html.Button("Submit", id="submit-button"),
                    ]
                ),
            ],
            style={"width": "20%", "display": "inline-block", "vertical-align": "top"},
        ),
        html.Div(
            [
                # Interactive Figure
                dcc.Graph(id="line-plot"),
            ],
            style={"width": "80%", "display": "inline-block", "vertical-align": "top"},
        ),
        # Chloropleth Map
        dcc.Graph(id="chloropleth-map"),
    ]
)


@app.callback(
    [Output("line-plot", "figure"), Output("chloropleth-map", "figure")],
    [
        Input("municipality-dropdown", "value"),
        Input("min-living-area-input", "value"),
        Input("max-living-area-input", "value"),
        Input("submit-button", "n_clicks"),
    ],
    [State("user-living-area-input", "value"), State("user-price-input", "value")],
)
def update_output(
    municipality,
    min_living_area,
    max_living_area,
    n_clicks,
    user_living_area_input,
    user_price_input,
):
    # Extract imputed values
    bl1 = df_imp["namedut"] == municipality
    bl2 = np.logical_and(
        df_imp["living_area"] >= min_living_area,
        df_imp["living_area"] <= max_living_area,
    )
    bl = np.logical_and(bl1, bl2)

    df_imp_subset = df_imp.loc[bl, :]

    expected_price_m2 = df_imp_subset["y_hat"].mean()

    # Include 1.5 and 2/3 of expected price as extremity indication
    low_expected_price_m2 = round(2 / 3 * expected_price_m2, 2)
    high_expected_price_m2 = round(1.5 * expected_price_m2, 2)

    # Extract observed values
    bl1 = df_actual["namedut"] == municipality
    bl2 = np.logical_and(
        df_actual["living_area"] >= min_living_area,
        df_actual["living_area"] <= max_living_area,
    )
    bl = np.logical_and(bl1, bl2)

    df_actual_subset = df_actual.loc[bl, :]

    actual_prices_m2 = df_actual_subset["price_m2"].to_list()

    info_df = df_actual_subset[
        [
            "listing_id",
            "price",
            "energy_class",
            "building_condition",
            "contact_type",
            "contact_name",
            "price_m2",
        ]
    ]

    hover_tmp = """
        Listing: %{customdata[0]}<br>
        Price m2: %{customdata[6]}<br>
        Price: %{customdata[1]}<br>
        Energy Class: %{customdata[2]}<br>
        Contact: %{customdata[4]}<br>
        Name Contact: %{customdata[5]}<br>
    """

    line_fig = go.Figure()
    line_fig.add_trace(
        go.Scatter(
            x=[expected_price_m2],
            y=[0],
            mode="markers",
            name="Expected Price per m2",
            hoverinfo="x",
        )
    )
    line_fig.add_trace(
        go.Scatter(
            x=[low_expected_price_m2, high_expected_price_m2],
            y=[0, 0],
            mode="markers",
            name="Low and High Prices",
            hoverinfo="x",
        )
    )

    if len(actual_prices_m2) > 0:
        line_fig.add_trace(
            go.Scatter(
                x=actual_prices_m2,
                y=[0 for _ in range(len(actual_prices_m2))],
                mode="markers",
                name="Actual prices per m2",
                opacity=0.2,
                customdata=info_df,
                hovertemplate=hover_tmp,
            )
        )

        # Add the user's point to the plot if user data has been submitted
    if n_clicks is not None:
        # Take in user data
        user_price_m2 = user_price_input / user_living_area_input

        line_fig.add_trace(
            go.Scatter(
                x=[user_price_m2], y=[0], mode="markers", name="Position", hoverinfo="x"
            )
        )

    # chloropeth map

    # Filter actual and imp dataset on living area (to allow comparison)
    bl = np.logical_and(
        df_imp["living_area"] >= min_living_area,
        df_imp["living_area"] <= max_living_area,
    )
    df_imp_filter = df_imp.loc[bl, :]
    df_imp_group = df_imp_filter.groupby("namedut")["y_hat"].mean().reset_index()

    bl = np.logical_and(
        df_actual["living_area"] >= min_living_area,
        df_actual["living_area"] <= max_living_area,
    )

    df_actual_filter = df_actual.loc[bl, :]

    columns_to_aggregate = ["price", "living_area", "namedut"]
    df_actual_filter = df_actual_filter[columns_to_aggregate]

    df_actual_group = df_actual_filter.groupby("namedut").agg(
        {"price": "mean", "living_area": "mean", "namedut": "count"}
    )
    df_actual_group = df_actual_group.rename({"namedut": "count"}, axis=1).reset_index()

    df_group = pd.merge(df_imp_group, df_actual_group, on="namedut", how="inner")
    df_group = gdf_municipalities.merge(df_group, on="namedut", how="inner")
    gdf_group = gpd.GeoDataFrame(df_group)

    map_fig = go.Figure(
        data=go.Choropleth(
            locations=[],
            z=[],
            text=[],
            geojson="http://geojson.io/",
        )
    )

    return line_fig, map_fig


@app.callback(
    Output("expected-price-per-month", "children"),
    [
        Input("municipality-dropdown", "value"),
        Input("min-living-area-input", "value"),
        Input("max-living-area-input", "value"),
    ],
)
def update_price_info(municipality, min_living_area, max_living_area):
    # Extract imputed values
    bl1 = df_imp["namedut"] == municipality
    bl2 = np.logical_and(
        df_imp["living_area"] >= min_living_area,
        df_imp["living_area"] <= max_living_area,
    )
    bl = np.logical_and(bl1, bl2)

    df_imp_subset = df_imp.loc[bl, :]

    middle_of_range = (min_living_area + max_living_area) // 2

    # Compute prices per month
    df_imp_subset["expected_price_per_month"] = (
        df_imp_subset["y_hat"] * df_imp_subset["living_area"]
    )

    # Find value closest to middle of range in subset data
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SettingWithCopyWarning)
        df_imp_subset["middle_area_delta"] = np.abs(
            df_imp_subset["living_area"] - middle_of_range
        )

    closest_index = np.argmin(df_imp_subset["middle_area_delta"])

    max_index = np.where(
        df_imp_subset["living_area"] == df_imp_subset["living_area"].max()
    )[0][0]
    min_index = np.where(
        df_imp_subset["living_area"] == df_imp_subset["living_area"].min()
    )[0][0]

    expected_price = df_imp_subset["expected_price_per_month"].iloc[closest_index]

    high_price = df_imp_subset["expected_price_per_month"].iloc[max_index]
    low_price = df_imp_subset["expected_price_per_month"].iloc[min_index]

    return html.Div(
        [
            html.H3("Expected Prices Per Month"),
            html.P(
                f"At {middle_of_range} m2, the expected price per month is: {expected_price}€"
            ),
            html.P(f"At {min_living_area} m2: {low_price:.2f}€ per month"),
            html.P(f"At {max_living_area} m2: {high_price:.2f}€ per month"),
        ]
    )


if __name__ == "__main__":
    update_output("Leuven", 50, 100, None, None, None)
    # update_price_info("Leuven", 50, 100)
    app.run_server(debug=True)
