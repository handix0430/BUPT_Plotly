##################### import #####################
import pandas as pd

import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State #dcc动态交互模块

import time
import datetime
#### Create app ####

app = Dash(__name__)
##################### Variable #####################

'''
配合Ctrl-F使用
interval-component 下一行的interval可以设置动画间隔秒数
'''

##################### Data #####################
df = pd.read_excel("CUC_Serv_Vehicle_Record.xlsx",nrows=100000)

##################### Cleanse #####################
#region Cleanse
#df = df.drop_duplicates()
df = df.loc[:, ["vehicle_plate","plate_color","lane_code","cross_time"]]#提取特定几列
df = df.fillna(0) #缺失值填0
df["plate_color"] = df["plate_color"].replace({"black":"黑","blue":"蓝","green":"绿","white":"白","yellow":"黄"}) # 替换不一致的值
df["lane_code"] = pd.to_numeric(df["lane_code"], errors="coerce") # 将ID列转换为数值类型，如果遇到无法转换的值，设为NULL
df["lane_code"] = df["lane_code"].fillna(0) # 将NULL值填充为0
df["lane_code"] = df["lane_code"].astype('category')

df["cross_time"] = pd.to_datetime(df["cross_time"]) # 转换时间
df["Date"] = df["cross_time"].dt.date # 提取日期
df["Time"] = df["cross_time"].dt.time # 提取时间
df.sort_values(by=['Date', 'Time'], inplace=True) # 按日期时间排序
df["Hour"] = df["cross_time"].dt.hour # 提取小时
df["HourMinute"] = pd.to_datetime(df["Time"], format='%H:%M:%S').dt.strftime('%H:%M')

# 按小时计算经过车辆总数
# hourly_count = df.groupby(df['cross_time'].dt.hour)['vehicle_plate'].count().reset_index(name="count")
# print(hourly_count.T)

#df.to_excel("CUC_Serv_Vehicle_Record_CLEANSE.xlsx")
#print(df)

#endregion


################ Figure ################
# figHeatmap = px.imshow(hourly_count.T, color_continuous_scale='Viridis')
# figHeatmap.update_layout(
#     xaxis_title="小时",
#     yaxis_title="日期",
#     title="每小时经过车辆总数热力图"
# )

##################### HTMLLayout #####################
Layout = html.Div(children=[
    #Header
    html.H1(children='毕设项目: 基于Plotly-Dash的动态数据分析系统'),
    html.H1(children='过车卡口数据分析'),
    html.H2(children='2019211121 2018210087 黄隽杰'),
    html.Br(),

    #Body

    ##Selector
    ###Date Picker
    html.P('请选择日期'),
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=df["Date"].min(),
        max_date_allowed=df["Date"].max(),
        initial_visible_month=df["Date"].max(),
        date=df["Date"].min(),
        display_format='YYYY-MM-DD',
    ),
    
    ###Interval
    html.Div([
        html.Button('▶️', id='play-button', n_clicks=0),
        html.Button('⏸', id='pause-button', n_clicks=0),
        dcc.Interval(
            id='interval-component',
            interval=3000, #设置时间
            n_intervals=0
        )
    ]),
    
    ###lane_code selector
    html.P('请选择欲查询的过道编号'),
    dcc.Checklist(
        id='lane-code-selector',
        options=[{'label': code, 'value': code} for code in sorted(df["lane_code"].unique())],
        value=list(df["lane_code"].unique())
    ),
    
    ###plate_color selector
    html.P('请选择欲查询的车牌颜色'),
    dcc.Checklist(
        id='color-selector',
        options=[{'label': x, 'value': x} for x in df['plate_color'].unique()],
        value=list(df['plate_color'].unique())
    ),

    ##Scatter
    dcc.Graph(id='Scatter'),

    ##Bar

    ##LineDate

    ##Heatmap
    dcc.Graph(id="heatmap"),

    ##LineTime
    dcc.Graph(id='LineTime'),

    ],
    #GlobalCSS
    style={'textAlign': 'center'}
)

##################### CALLBACK #####################

########## ScatterCallback ##########
@app.callback(
    Output('Scatter', 'figure'),
    [Input('date-picker', 'date'), Input('color-selector', 'value'), Input('lane-code-selector', 'value')]
)
def update_figure_Scatter(selected_date, selected_color, selected_lanes):
    selected_date = pd.to_datetime(selected_date, format='%Y-%m-%d')
    filtered_data_scatter = df[(df['Date'] == selected_date) & (df['plate_color'].isin(selected_color)) & (df["lane_code"] .isin(selected_lanes))]
    #print(df["HourMinute"])
    
    #filtered_data_scatter = filtered_data_scatter.sort_values(by='Time') # 按照时间排序
    #print(filtered_data_scatter)
    figScatter = px.scatter(
        filtered_data_scatter,
        x="HourMinute",
        y='lane_code',
        color='plate_color',
        color_discrete_map={
                "total": "#d62728",
                "白": "#b0b0b0",
                "绿": "#009946",
                "蓝": "#3e81e9",
                "黄": "#fbc90a",
                "黑": "black",
            },
        hover_data=['Date','vehicle_plate','plate_color'],
        title=f'{selected_date.date()} 各个过道路过的车子',
        labels={'HourMinute':'时间','Time': '时间', 'lane_code': '过道编号','Date':'日期','vehicle_plate':'车牌号','plate_color':'车牌颜色'},
        category_orders={"lane_code": sorted(filtered_data_scatter["lane_code"].unique())},
        height=500,
        opacity=0.85,
    )
    times = pd.date_range(start="00:00:00", end="23:59:59", freq="H")
    times = times.strftime("%H:%M")

    figScatter.update_xaxes(
        title="时间",
        )
    figScatter.update_yaxes(title="过道编号",type="category")
    figScatter.update_layout(title={'x': 0.5}, xaxis_nticks=24)
    return figScatter

########## LineTimeCallback ##########
@app.callback(
    Output('LineTime', 'figure'),
    [Input('date-picker', 'date'), Input('color-selector', 'value'), Input('lane-code-selector', 'value')]
)
def update_figure_LineTime(selected_date, selected_color, selected_lanes):
    selected_date = pd.to_datetime(selected_date, format="%Y-%m-%d")
    filtered_data_time = df[(df["Date"] == selected_date) & (df['plate_color'].isin(selected_color)) & (df["lane_code"] .isin(selected_lanes))]
    #filtered_data_time = df

    if filtered_data_time.empty:
        figLineTime = px.line()
        print("Empty")
    else:
        agg_data = filtered_data_time.groupby(["plate_color","Hour"], as_index=False)["vehicle_plate"].count()
        agg_data = agg_data.rename(columns={"vehicle_plate":"count"})
        #print(agg_data)

        #Total
        total_data = agg_data.groupby("Hour", as_index=False)["count"].sum()
        total_data["plate_color"] = "total"
        #print(agg_data)
        agg_data = pd.concat([agg_data,total_data])
        #print(agg_data)

        figLineTime = px.line(
            agg_data, 
            x="Hour", 
            y="count",
            color="plate_color",
            color_discrete_map={
                "total": "#d62728",
                "白": "#b0b0b0",
                "绿": "#009946",
                "蓝": "#3e81e9",
                "黄": "#fbc90a",
                "黑": "black",
            },
            markers=True, 
            text="count",
            )
        figLineTime.update_layout(title={
            'text': f" {selected_date.date()} 每小时经过的车数量",
            'x': 0.5,
            'xanchor': 'center'
        })

        times = pd.date_range(start="00:00:00", end="23:59:59", freq="H")
        times = times.strftime("%H:%M")

        figLineTime.update_xaxes(
            title="时间",
            tickmode='array',
            tickvals=list(range(24)),
            ticktext=times,
            tickformat='%H:%M', # 添加此参数来设置时间格式
            )
        figLineTime.update_yaxes(title="车数量（台）")
        figLineTime.update_traces(
            selector=dict(name='total'),
            line=dict(width=5),
            marker=dict(size=10),
            textfont={"color": "red"},
            textposition="top center"
        )

        # 对其他 trace 进行默认的设置
        figLineTime.update_traces(
            selector=dict(name=lambda x: x != 'total'),
            line=dict(width=3),
            marker=dict(size=5),
            textposition="top center"
        )
    return figLineTime

########## LineDateCallback ##########

########## HeatmapCallback ##########
@app.callback(
    Output("heatmap", "figure"),
    [Input('date-picker', 'date'), Input('color-selector', 'value')]
)
def update_heatmap(selected_date, selected_color):
    selected_date = pd.to_datetime(selected_date, format='%Y-%m-%d')
    filtered_data_heatmap = df[(df['cross_time'].dt.date == selected_date.date()) & (df["plate_color"].isin(selected_color))]
    #hourly_count = filtered_data_heatmap.groupby(filtered_data_heatmap['cross_time'].dt.hour)['vehicle_plate'].count().reset_index(name="count")
    hourly_count = filtered_data_heatmap.groupby(['lane_code','Hour']).size().reset_index(name="count")
    heatmap_data = hourly_count.pivot(index='lane_code', columns='Hour', values='count').fillna(0)
    #print(hourly_count)
    figHeatmap = px.imshow(
        heatmap_data,
        labels={'y':'过道编号','x':'时间','color':'车辆总数'},
        color_continuous_scale='redor',
        text_auto=True,
        )
    figHeatmap.update_layout(
        xaxis_title="时间/小时",
        title={'text': f"{selected_date.date()} 各个过道每小时热力图",'x':0.5,'xanchor':'center'},
    )
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

########## DatePickerCallback ##########
@app.callback(
    Output("date-picker","date"),
    [Input('interval-component','n_intervals')],
    [State('date-picker','date')]
)
def update_Date(n, current_date):
    next_date = datetime.datetime.strptime(current_date, '%Y-%m-%d') + datetime.timedelta(days=1)
    return next_date.strftime('%Y-%m-%d')

########## ControlAnimationCallback ##########
@app.callback(
    Output('interval-component', 'disabled'),
    [Input('play-button', 'n_clicks'), Input('pause-button', 'n_clicks')],
    [State('interval-component', 'disabled')]
)
def control_animation(play_clicks, pause_clicks, interval_disabled):
    # 如果点击播放按钮，则禁用Interval组件以启动动画
    if play_clicks > pause_clicks:
        return False
    # 如果点击暂停按钮，则启用Interval组件以暂停动画
    else:
        return True

##################### MAIN #####################
if __name__ == "__main__":
   app.layout = Layout
   app.run_server(debug=True)