import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd 
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
    # Here goes the logic of backend data processing 
    # for example, we're just making a mock figure
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=[1, 2, 3],
        y=[4, 5, 6],
        mode='lines+markers',
    ))

    # Mock chloropeth map, replace with actual data
    map_fig = go.Figure(data=go.Choropleth(
        locations=[],
        z=[],
        text=[],
        geojson="http://geojson.io/",
    ))

    return line_fig, map_fig

if __name__ == '__main__':
    app.run_server(debug=True)