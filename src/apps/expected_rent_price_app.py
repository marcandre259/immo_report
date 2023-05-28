import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        # Filters
        html.Div([
            html.H3("Filters"),
            dcc.Dropdown(
                id='municipality-dropdown',
                options=[],  # To be filled with the municipalities data
                placeholder="Select a Municipality",
            ),
            dcc.RangeSlider(
                id='living-area-slider',
                min=0, max=100,  # To be filled with the appropriate living area range
                step=1,
                value=[20, 80],
                marks={
                    0: '0',
                    50: '50',
                    100: '100'
                }
            )
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
     Input('living-area-slider', 'value')]
)
def update_output(municipality, living_area):
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
