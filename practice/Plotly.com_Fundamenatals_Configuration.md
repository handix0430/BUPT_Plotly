能放大缩小
config = dict({'scrollZoom': True})
禁用交互
config = {'responsive': False}
静态图
config = {'staticPlot': True}
固定modbar
config = {'displayModeBar': False}
隐藏logo
config = {'displaylogo': False}
增加可绘制按钮
fig.update_layout(
    dragmode='drawopenpath',
    newshape_line_color='cyan',
    modebar_add=['drawline',
        'drawopenpath',
        'drawclosedpath',
        'drawcircle',
        'drawrect',
        'eraseshape'
       ]
)