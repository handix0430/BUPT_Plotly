##################### import #####################
import pandas as pd

import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State #dcc动态交互模块

import re
import base64
import io
#### Create app ####

app = Dash(__name__)
##################### Variable #####################

'''
配合Ctrl-F使用
interval-component 下一行的interval可以设置动画间隔秒数
'''

##################### Data #####################

df = pd.read_excel("CUP_SNAP_HISTORYRECORD.xlsx")

##################### Cleanse #####################
#region Cleanse
#df = df.drop_duplicates()
def Cleanse_df(df):
    df = df.loc[:, ["sex","age","snap_cam_name","snap_id","snap_time"]]#提取特定几列
    df = df.fillna(0) #缺失值填0

    # 门禁摄像头名称改名,只保留位置和进出
    pattern = re.compile(r'人脸-?\d+|-?\d+')
    df["snap_cam_name"] = df["snap_cam_name"].apply(lambda x: re.sub(pattern, '', x))

    # df["snap_cam_name"] = df["snap_cam_name"].replace({}) # 替换值
    # df["lane_code"] = pd.to_numeric(df["lane_code"], errors="coerce") # 将ID列转换为数值类型，如果遇到无法转换的值，设为NULL
    # df["lane_code"] = df["lane_code"].fillna(0) # 将NULL值填充为0
    #df["snap_time"] = df["snap_time"].astype('category')
    df["sex"] = df["sex"].astype('category')

    df["snap_time"] = pd.to_datetime(df["snap_time"]) # 转换时间
    df["date"] = df["snap_time"].dt.date # 提取日期
    df["time"] = df["snap_time"].dt.time # 提取时间
    #df.sort_values(by=['Date', 'Time'], inplace=True) # 按日期时间排序
    df["hour"] = df["snap_time"].dt.hour # 提取小时
    #df["time"] = pd.to_datetime(df["time"], format='%H:%M:%S').dt.strftime('%H:%M')
    df["time"] = pd.to_datetime(df["time"], format='%H:%M:%S')
    return df

df=Cleanse_df(df)
#print(df)
#endregion


################ Figure ################


##################### HTMLLayout #####################
Layout = html.Div(children=[
    #Header
    html.H1(children='毕设项目: 基于Plotly-Dash的动态数据分析系统'),
    html.H1(children='人脸识别门禁数据分析'),
    html.H2(children='2019211121 2018210087 黄隽杰'),
    html.Br(),

    #Body

    ##Selector
    ##Upload

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            '拖拽文件至此或',
            html.A('点击选择文件'),
            '以更新数据'
        ]),
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
        accept='.csv,.xls,.xlsx,.txt',
        multiple=False
    ),
    html.Div(id='output-data-upload'),

    
    ###Interval
    # html.Div([
    #     html.Button('▶️', id='play-button', n_clicks=0),
    #     html.Button('⏸', id='pause-button', n_clicks=0),
    #     dcc.Interval(
    #         id='interval-component',
    #         interval=5000, #设置时间
    #         n_intervals=0
    #     )
    # ]),
    
    html.Br(),

    ###place selector
    html.P('请选择欲查询的位置'),
    dcc.Dropdown(
        id='place_selector',
        options=[{'label': code, 'value': code} for code in sorted(df["snap_cam_name"].unique())],
        value=list(df["snap_cam_name"].unique()),
        multi=True
    ),
    html.Br(),
    ###sex selector
    html.P('请选择欲查询的性别'),
    dcc.Checklist(
        id='sex_selector',
        #options=[{'label': x, 'value': x} for x in df['sex'].unique()],
        options = [{'label':'女', 'value':0},{'label':'男', 'value':1}],
        value=list(df['sex'].unique())
    ),

    ##Scatter
    dcc.Graph(id='Scatter'),

    ##Bar
    dcc.Dropdown(
        id='hour_selector',
        options=[
            {'label': '全部', 'value': 'all'},
            {'label': '13:00-14:00', 'value': '13'},
            {'label': '14:00-15:00', 'value': '14'},
            {'label': '15:00-16:00', 'value': '15'},
        ],
        value='all',
        #placeholder='选择小时',
        #style={'width': '200px'}
    ),
    dcc.Graph(id='bar'),
    ##Line

    ##Heatmap
    dcc.Graph(id="heatmap"),

    ],
    #GlobalCSS
    style={'textAlign': 'center'}
)

##################### CALLBACK #####################

########## ScatterCallback ##########
@app.callback(
    Output('Scatter', 'figure'),
    [Input('sex_selector', 'value'), Input('place_selector', 'value')],
)
def update_scatter(selected_sex, selected_place):
    filtered_data_scatter = df[(df["sex"].isin(selected_sex)) & (df["snap_cam_name"] .isin(selected_place))]
    figScatter = px.scatter(
        filtered_data_scatter,
        x="snap_time",
        y='snap_cam_name',
        color='sex',
        color_discrete_sequence=["red","blue"],
        size="age",
        hover_data=['snap_id','sex','age','snap_cam_name','snap_time'],
        title='各个区域在2020/11/5下午进出情况',
        labels={'sex':'性别','snap_time': '时间', 'snap_cam_name': '地点','age':'年龄','snap_id':'人员编号'},
        #width=10000,
        height=800,
        opacity=0.4,
    )
    figScatter.update_xaxes(
        title="时间",
        )
    figScatter.update_yaxes(title="区域",type="category")
    figScatter.update_layout(title={'x': 0.5}, xaxis_nticks=24)
    return figScatter

########## BarCallback ##########
@app.callback(
    Output("bar", "figure"),
    [Input('sex_selector', 'value'), Input('place_selector', 'value'),Input('hour_selector', 'value')]
)
def update_bar(selected_sex, selected_place,selected_hour):
    if selected_hour == 'all':
        filtered_data_bar = df[(df["sex"].isin(selected_sex)) & (df["snap_cam_name"] .isin(selected_place))]  
    else:
        filtered_data_bar = df[(df["sex"].isin(selected_sex)) & (df["snap_cam_name"] .isin(selected_place)) & (df["hour"]==int(selected_hour))]
        #filtered_data_bar = df[(df["hour"]==selected_hour)]
        #print(filtered_data_bar)
    # print(selected_hour)
    # print(df[df["hour"]==int(selected_hour)])
    #filtered_data_bar = df[(df["sex"].isin(selected_sex)) & (df["snap_cam_name"] .isin(selected_place)) & (df["hour"] == selected_hour)]  
    #filtered_data_bar['age'] = filtered_data_bar['age'].apply(lambda x: 17 if x < 18 else x)
    filtered_data_bar['age_group'] = pd.cut(
        filtered_data_bar['age'], 
        bins=[0,18, 28, filtered_data_bar['age'].max()], 
        labels=['<18', '18-28', '>28'],
        right=False
        )
    #print(filtered_data_bar['age_group'].value_counts())
    #filtered_data_bar = filtered_data_bar.dropna(subset=['age_group'])
    figBar = px.histogram(
        filtered_data_bar, 
        x="snap_cam_name", 
        color="age_group",
        nbins=10, 
        opacity=0.75,
        #barmode="group",
        labels={'age_group':'分类','snap_cam_name': '地点', 'count': '人数'},
        )
    figBar.update_layout(
        xaxis_title_text='年龄',
        yaxis_title_text='人数',
        title={
            'text': '人员年龄分布柱状图',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        bargap=0.2,
        bargroupgap=0.1,
    )
    return figBar

########## HeatmapCallback ##########
@app.callback(
    Output("heatmap", "figure"),
    [Input('sex_selector', 'value'), Input('place_selector', 'value')]
)
def update_heatmap(selected_sex,selected_place):
    filtered_data_heatmap = df[(df["sex"].isin(selected_sex)) & (df["snap_cam_name"] .isin(selected_place))]
    hour_count = filtered_data_heatmap.groupby(['snap_cam_name','hour']).size().reset_index(name="count")
    heatmap_data = hour_count.pivot(index='snap_cam_name', columns='hour', values='count').fillna(0)
    #print(hour_count)
    figHeatmap = px.imshow(
        heatmap_data,
        labels={'y':'位置','x':'时间','color':'进出人总数'},
        color_continuous_scale='redor',
        text_auto=True,
        height=1000,
        )
    # figHeatmap.update_layout(
    #     xaxis_title="时间/小时",
    #     title={'text': f"{selected_date.date()} 各个过道每小时热力图",'x':0.5,'xanchor':'center'},
    # )
    times = pd.date_range(start="00:00:00", end="23:59:59", freq="H")
    times = times.strftime("%H:%M")

    figHeatmap.update_xaxes(
        title="时间",
        tickmode='array',
        tickvals=list(range(24)),
        ticktext=times,
        tickformat='%H:%M', # 添加此参数来设置时间格式
        )
    figHeatmap.update_yaxes(title="过道编号",type="category")
    return figHeatmap


########## UploadCallback ##########
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),Input('sex_selector', 'value'), Input('place_selector', 'value'),Input('hour_selector', 'value')],
              State('upload-data', 'filename'))

def update_dataframe(contents, filename,selected_sex,selected_place,selected_hour):
    global df
    if contents is not None:
        # 解析上传的CSV文件，存储到DataFrame中
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df_upload = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' or 'xlsx' in filename:
                df_upload = pd.read_excel(io.BytesIO(decoded))
            else:
                return html.Div([
                    '不支持该档案。目前支持xls、xlsx、csv'
                ])
        except Exception as e:
            print(e)
            return html.Div([
                'Error.'
            ])
        df=Cleanse_df(df_upload)
        #print(df)
        return html.Div([
            '上传成功！',
        ])
    else:
        return html.Div([
            '请上传档案以更新'
        ])
# print(df)
##################### MAIN #####################
if __name__ == "__main__":
   app.layout = Layout
   app.run_server(debug=True)