import pandas as pd

#Upload
import base64 
import io
import requests

import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State #dcc动态交互模块
import dash_bootstrap_components as dbc #美化

# Create Dash APP(bootstrap css style)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])  

######################### Data ###########################

# Data
## Built-In
df = px.data.iris()

## Local
#df = pd.read_csv("iris.data.csv")

## Online
#url = 'https://www.gairuo.com/file/data/dataset/iris.data'
#df = pd.read_html(url)


# Variable


######################### Figure ###########################

##figScatter
figScatter = px.scatter(
    df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    size='petal_length',
    hover_data=['petal_width'],
    title="鸢尾花数据散点图"
)

##figBar
figBar = px.bar(
    df,
    x="species",
    y=["sepal_width", "sepal_length", "petal_width", "petal_length"],
    barmode="group",
    height=500,
    title="鸢尾花数据柱状图",
    #text="value"
)

##figHeatmap
corr_matrix=df.corr(numeric_only=True)
figHeatmap = px.imshow(corr_matrix.values,
                x=corr_matrix.index,
                y=corr_matrix.columns,
                color_continuous_scale='RdBu',
                zmin=-1,
                zmax=1,
                #text_auto=True
                )

####################### Layout #############################

# HTMLLayout
Layout = html.Div(children=[
    #Header
    html.H1(children='毕设项目: 基于Plotly-Dash的动态数据分析系统'),
    html.H2(children='2019211121 2018210087 黄隽杰'),

    html.Br(),

    ## Upload
    html.H3(children='上传模块',style={'color': 'red'}),

    ### OnlineData
    dcc.Input(id='input-url', type='text', placeholder='输入数据URL'),
    html.Button('读取数据', id='submit-url'),


    ### LocalCSV
    dcc.Upload(
    id='upload',
    children=html.Div([html.A('点击上传或将文件拖入此区域')]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
            },
    #multiple=True #多文件上传
    ),

    ## UploadOutput
    html.H3(children='上传输出内容',style={'color': 'red'}),

    html.Div([
        dash_table.DataTable(id='datatable', editable=True,
                             style_cell={'fontSize': 20, 'font-family': 'sans-serif'})
    ], style={'width': '20%'}),     



    #Body
    html.Br(),
    ##Scatter
    html.H3(children='散列图模块',style={'color': 'red'}),

    dcc.Graph(id='Scatter', figure=figScatter),

    html.P("Filter by petal width:"),

    dcc.RangeSlider(
        id='RangeSliderScatter',
        min=0, max=2.5, step=0.1,
        marks={0: '0',0.5:'0.5', 1:'1',1.5:'1.5',2:'2',2.5: '2.5'},
        value=[df['petal_width'].min(), df['petal_width'].max()]
    ),



    ##Bar
    html.H3(children='柱状图模块',style={'color': 'red'}),

    ##BarDropdown
    html.P(style={'margin-top':'40px','margin-bottom':'40px'}),

    html.P("Filter by species:"),

    dcc.Dropdown(
        id='species-dropdown',
        options=[{'label': i, 'value': i} for i in ['all']+list(df['species'].unique())],
        value='all'
    ),

    dcc.Graph(id='Bar', figure=figBar),



    ##Heatmap
    html.H3(children='关系热图模块',style={'color': 'red'}),

    dcc.Graph(id='Heatmap',figure=figHeatmap)
    
    ],
    #GlobalCSS
    style={'textAlign': 'center'}
)
app.layout = Layout

################## Callback ##################################
##OnlineData
# @app.callback(
#     [Output('Scatter', 'figure'), 
#     Output('Bar', 'figure'),
#     Output('Heatmap', 'figure')],
#     [Input('submit-url', 'n_clicks')],
#     [State('input-url', 'value')]
#     )
# def update_figure(n_clicks, url):
#     if not url:
#         return {}

#     # 从URL读取数据
#     try:
#         response = requests.get(url)
#         df = pd.read_csv(io.StringIO(response.text))
#     except:
#         return {}

##table
@app.callback(
    Output('datatable', 'data'),
    Output('datatable', 'columns'),
    Input('upload', 'contents'),
    State('upload', 'filename'),
    prevent_initial_call=True
)
def update_datatable(contents, filename):
    """上传文件后更新表格"""
    print(1)
    if not contents:
        return [{}], []
    df = None
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        df = pd.read_excel(io.BytesIO(decoded))
    elif 'txt' in filename:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')

    if df is None:
        return [{}],[]
    
    #cleanse

    ##删除缺失值
    df.dropna(inplace=True)

    ##检查异常值
    for col in df.columns[:-1]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        #print(f"{col}: {len(outliers)} outliers")

    ##替换异常值为中位数
    for col in df.columns[:-1]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df[col] = df[col].apply(lambda x: df[col].median() if x < lower_bound or x > upper_bound else x)
    
    ##转换数据
    df['species'] = df['species'].astype('category')
    df['sepal_width'] = df['sepal_width'].astype(float)
    df['sepal_length'] = df['sepal_length'].astype(float)
    df['petal_width'] = df['petal_width'].astype(float)
    df['petal_length'] = df['petal_length'].astype(float)


    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]



##ScatterSlider
@app.callback(
    Output("Scatter", "figure"), 
    Input("RangeSliderScatter", "value")
    )
def update_Scatter_fig(slider_range):
    low, high = slider_range
    mask = (df['petal_width'] > low) & (df['petal_width'] < high)
    figScatter = px.scatter(
        df[mask],
        x="sepal_width",
        y="sepal_length",
        color="species",
        size='petal_length',
        hover_data=['petal_width']
        )
    return figScatter



##BarDropdown
@app.callback(
    Output('Bar', 'figure'),
    Input('species-dropdown', 'value')
)
def update_species_bar(species):
    if species == 'all':
        filtered_df = df
        title = "鸢尾花数据柱状图"
    else:
        filtered_df = df[df['species'] == species]
        title = f' {species.capitalize()} 种类数据柱状图'
    figBar = px.bar(
        filtered_df,
        x='species',
        y=["sepal_width", "sepal_length", "petal_width", "petal_length"],
        title=title,
        barmode="group"
    )
    return figBar



## Heatmap

########################## MAIN ##########################
if __name__ == '__main__':
    # run（热更新）
    app.run_server(debug=True)
