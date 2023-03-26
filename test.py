import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# Load iris dataset
df = px.data.iris()

# Define app
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1('Iris Heatmap'),
    html.Div([
        html.Label('X-axis'),
        dcc.Dropdown(
            id='x-axis-dropdown',
            options=[{'label': i, 'value': i} for i in df.columns[:-1]],
            value='sepal_width'
        ),
        html.Label('Y-axis'),
        dcc.Dropdown(
            id='y-axis-dropdown',
            options=[{'label': i, 'value': i} for i in df.columns[:-1]],
            value='petal_length'
        ),
        html.Label('Color'),
        dcc.Dropdown(
            id='color-dropdown',
            options=[{'label': i, 'value': i} for i in df.columns[:-1]],
            value='sepal_length'
        ),
        html.Label('Aggregation'),
        dcc.Dropdown(
            id='agg-dropdown',
            options=[
                {'label': 'Average', 'value': 'mean'},
                {'label': 'Minimum', 'value': 'min'},
                {'label': 'Maximum', 'value': 'max'}
            ],
            value='mean'
        ),
    ], style={'width': '50%', 'margin': 'auto'}),
    dcc.Graph(id='heatmap')
])