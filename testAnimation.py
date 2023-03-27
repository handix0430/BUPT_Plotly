import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('data.csv')

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(
        id='graph-update',
        interval=1000,  # 每隔1秒更新一次
        n_intervals=0
    )
])

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    # 取最新的100行数据
    data = df[-100:]

    # 创建散点图
    scatter = go.Scatter(
        x=data['x'],
        y=data['y'],
        mode='lines+markers'
    )

    # 设置图形布局
    layout = go.Layout(
        xaxis=dict(range=[min(data['x']), max(data['x'])]),
        yaxis=dict(range=[min(data['y']), max(data['y'])]),
    )

    # 返回图形
    return {'data': [scatter], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
