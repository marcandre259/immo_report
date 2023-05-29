import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

import warnings

import pandas as pd 
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

municipality_names = list(np.sort(df_actual["namedut"].unique()))

max_living_area = int(df_actual["living_area"].max() // 1000 * 2000)
min_living_area = int(df_actual["living_area"].min() // 10 * 10)

## layout
app.layout = html.Div([
    html.Div([
        # Filters
        html.Div([
            html.H3("Filters"),
            dcc.Dropdown(
                id='municipality-dropdown',
                value="Leuven",
                options=municipality_names,  # To be filled with the municipalities data
                placeholder="Select a Municipality",
            ),
             html.Div([
                html.Label('Living Area Range (m2):'),
                html.Div([
                    dcc.Input(
                        id='min-living-area-input',
                        type='number',
                        value=min_living_area,
                        min=min_living_area,
                        max=max_living_area,
                        step=5,
                        placeholder="Min Living Area"
                    ),
                    dcc.Input(
                        id='max-living-area-input',
                        type='number',
                        value=max_living_area,
                        min=min_living_area,
                        max=max_living_area,
                        step=5,
                        placeholder="Max Living Area"
                    ),
                ], style={'display': 'flex', 'justify-content': 'space-between'})
            ]),

        ], className="menu"),
        html.Div(id="expected-price-per-month"),
    ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        # Interactive Figure
        dcc.Graph(id='line-plot'),
    ], style={'width': '80%', 'display': 'inline-block', 'vertical-align': 'top'}),

    # Chloropleth Map
    dcc.Graph(id='chloropleth-map'),

])

@app.callback(
    [Output('line-plot', 'figure'),
     Output('chloropleth-map', 'figure')],
    [Input('municipality-dropdown', 'value'),
     Input('min-living-area-input', 'value'),
     Input('max-living-area-input', 'value')]
)
def update_output(municipality, min_living_area, max_living_area):
    # Extract imputed values
    bl1 = (df_imp["namedut"] == municipality)
    bl2 = np.logical_and(df_imp["living_area"] >= min_living_area, df_imp["living_area"] <= max_living_area)
    bl = np.logical_and(bl1, bl2)

    df_imp_subset = df_imp.loc[bl, :]

    expected_price_m2 = df_imp_subset["y_hat"].mean()

    # Include 1.5 and 2/3 of expected price as extremity indication 
    low_expected_price_m2 = round(2/3 * expected_price_m2, 2)
    high_expected_price_m2 = round(1.5 * expected_price_m2, 2)

    # Extract observed values 
    bl1 = (df_actual["namedut"] == municipality)
    bl2 = np.logical_and(df_actual["living_area"] >= min_living_area, df_actual["living_area"] <= max_living_area)
    bl = np.logical_and(bl1, bl2)

    df_actual_subset = df_actual.loc[bl, :]

    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=[expected_price_m2],
        y=[0],
        mode='markers',
        name="Expected Price"
    ))
    line_fig.add_trace(go.Scatter(
        x=[low_expected_price_m2, high_expected_price_m2],
        y=[0, 0],
        mode="markers",
        name="Low and High Prices",
    ))

    # Mock chloropeth map, replace with actual data
    map_fig = go.Figure(data=go.Choropleth(
        locations=[],
        z=[],
        text=[],
        geojson="http://geojson.io/",
    ))

    return line_fig, map_fig

@app.callback(
    Output('expected-price-per-month', 'children'),
    [Input('municipality-dropdown', 'value'),
     Input('min-living-area-input', 'value'),
     Input('max-living-area-input', 'value')]
)
def update_price_info(municipality, min_living_area, max_living_area):
    # Extract imputed values
    bl1 = (df_imp["namedut"] == municipality)
    bl2 = np.logical_and(df_imp["living_area"] >= min_living_area, df_imp["living_area"] <= max_living_area)
    bl = np.logical_and(bl1, bl2)

    df_imp_subset = df_imp.loc[bl, :]
    
    middle_of_range = (min_living_area + max_living_area) // 2

    # Compute prices per month
    df_imp_subset["expected_price_per_month"] = df_imp_subset["y_hat"] * df_imp_subset["living_area"]

    # Find value closest to middle of range in subset data 
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SettingWithCopyWarning)
        df_imp_subset["middle_area_delta"] = np.abs(df_imp_subset["living_area"] - middle_of_range)

    closest_index = np.argmin(df_imp_subset["middle_area_delta"])

    max_index = np.where(df_imp_subset["living_area"] == df_imp_subset["living_area"].max())[0][0]
    min_index = np.where(df_imp_subset["living_area"] == df_imp_subset["living_area"].min())[0][0]

    expected_price = df_imp_subset["expected_price_per_month"].iloc[closest_index]

    high_price = df_imp_subset["expected_price_per_month"].iloc[max_index]
    low_price = df_imp_subset["expected_price_per_month"].iloc[min_index]

    return html.Div([
        html.H3("Expected Prices Per Month"),
        html.P(f"At {middle_of_range} m2, the expected price per month is: {expected_price}€"),
        html.P(f"At {min_living_area} m2: {low_price:.2f}€ per month"),
        html.P(f"At {max_living_area} m2: {high_price:.2f}€ per month"),
    ])

if __name__ == '__main__':
    # update_output("Leuven", 50, 100)
    # update_price_info("Leuven", 50, 100)
    app.run_server(debug=True)