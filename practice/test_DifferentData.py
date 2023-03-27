import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

# 数据加载
df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

# Dash app定义
app = dash.Dash(__name__)

# 页面布局
app.layout = html.Div([
    html.H1(children='在线数据分析展示'),

    html.Div(children='''
        选择数据类型
    '''),

    dcc.Dropdown(
        id='data-type',
        options=[
            {'label': '鸢尾花数据', 'value': 'iris'},
            {'label': '波士顿房价数据', 'value': 'boston'}
        ],
        value='iris'
    ),

    dcc.Graph(id='graph')
])

# 回调函数
@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('data-type', 'value')])
def update_figure(selected_value):
    if selected_value == 'iris':
        fig = px.scatter(df, x="sepal_length", y="sepal_width", color="species")
    else:
        boston = pd.read_csv('https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv')
        fig = px.scatter(boston, x="rm", y="medv")
    return fig

# 运行应用
if __name__ == '__main__':
    app.run_server(debug=True)

#这个例子中，我们通过一个下拉框来选择数据类型（鸢尾花数据或波士顿房价数据），
# 然后根据选择的数据类型来更新展示图表。
# 在回调函数中，我们加载了数据，然后根据数据类型生成对应的图表，最后将图表返回给页面。
# 可以通过修改回调函数中的数据处理逻辑，来实现更复杂的在线数据分析功能。