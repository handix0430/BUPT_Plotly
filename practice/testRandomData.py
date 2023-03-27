import dash

from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
import numpy as np

# 定义应用程序
app = dash.Dash(__name__)

# 定义布局
app.layout = html.Div(children=[
    html.H1(children='随机数据模拟'),
    html.Div(children='''
        选择要生成的数据类型和数量：
    '''),
    dcc.Dropdown(
        id='datatype-dropdown',
        options=[
            {'label': '整数', 'value': 'int'},
            {'label': '浮点数', 'value': 'float'},
            {'label': '正态分布', 'value': 'normal'},
            {'label': '均匀分布', 'value': 'uniform'}
        ],
        value='int'
    ),
    dcc.Input(
        id='data-count-input',
        type='number',
        placeholder='输入数量',
        value=10
    ),
    html.Br(),
    html.Button('生成数据', id='data-button', n_clicks=0),
    html.Br(),
    html.Div(id='data-output')
])

# 定义回调函数
@app.callback(
    Output('data-output', 'children'),
    [Input('data-button', 'n_clicks')],
    [State('datatype-dropdown', 'value'),
     State('data-count-input', 'value')])
def generate_data(n_clicks, datatype, data_count):
    if n_clicks > 0:
        if datatype == 'int':
            data = np.random.randint(0, 100, data_count)
        elif datatype == 'float':
            data = np.random.rand(data_count)
        elif datatype == 'normal':
            data = np.random.normal(0, 1, data_count)
        elif datatype == 'uniform':
            data = np.random.uniform(0, 1, data_count)

        df = pd.DataFrame(np.random.randint(0, 100, size=(int(data_count), 2)), columns=['Index', 'Value'])
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
                ]) for i in range(len(df))
            ])
        ])
        return table

# 运行应用程序
if __name__ == '__main__':
    app.run_server(debug=True)
