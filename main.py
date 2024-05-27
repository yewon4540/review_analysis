from dash import Dash, dcc, html, Input, Output, State
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash_table
import warnings
import json
import re

warnings.filterwarnings('ignore')

senti_df = pd.read_csv('./data/senti_df.csv',sep="\t")
# senti_df['감정 점수'] = senti_df['감정 점수']*100
words_list = ['test']

app = Dash(__name__)

app.layout = html.Div([
    html.H4(f'HRD-net 후기데이터'),
    dcc.Graph(id='graph'),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    dcc.RangeSlider(
        id='score-slider',
        min=45,
        max=100,
        step=1,  # 1점 단위
        value=[80, 85]
    ),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    dcc.Checklist(
        id="checklist",
        options=['긍정','부정','중립'],
        value=['긍정'],
        inline=True,
        inputStyle={"width": "20px", "height": "20px"},
        labelStyle={"fontSize":"20px"}
    ),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    dcc.RadioItems(
        id="radioItems",
        options=['과정종합점수', '감정 점수'],
        value="과정종합점수",
        inline=True,
        inputStyle={"width": "20px", "height": "20px"},
        labelStyle={"fontSize":"20px"}
    ),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    html.Div([
        # html.Label("빈출어 View 범위 : "),
        # dcc.Input(id="noun_counts_min", type='number', value=1, style={"width": "200px", "height": "40px", "fontSize": "20px"},),
        # html.Span([html.Br(style={"line-height": "40"})]),
        # html.Span([html.Br(style={"line-height": "40"})]),
        html.Label("명사 View 최대값 : "),
        dcc.Input(id="noun_counts_max", type='number', value=10, style={"width": "200px", "height": "40px", "fontSize": "20px"},)
    ], 
        
        style={"fontSize":"20px"}),
    html.Button('갱신하기', 
                id='update-button', 
                n_clicks=0, 
                style={"display":"block", "margin":"10px auto 0", "fontSize":"40px", "width": "600px", "height": "100px",}),
    
    html.Hr(style={"width": "100%", "height": "3px", "backgroundColor": 'black'}),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    html.A("네트워크 그래프 확인", href="http://10.40.1.109:9091/", style={"fontSize": "20px", "margin": "10px","margin-bottom":"10px"}),
    
    html.Hr(style={"width": "100%", "height": "3px", "backgroundColor": 'black'}),
    dcc.Dropdown(
        id='category-dropdown2',
        options=[{'label': words_, 'value': words_} for words_ in words_list],
        value=words_list[0],
        style={"width": "300px", "height": "50px", "display":"block", "margin":"10px auto 0"}
    ),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    dcc.Checklist(
        id="column_list",
        options=['검색어','훈련명','훈련기관','과정종합점수','문장', '결과'],
        value=['문장'],
        inline=True,
        inputStyle={"width": "20px", "height": "20px"},
        labelStyle={"fontSize":"20px"}
        ),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    html.Div([
        html.Button("현재 표 다운하기", id="btn_txt", style={"display":"block", "margin":"auto", "fontSize":"15px"}),
        dcc.Download(id="download-text-index"),
    ]),
    
    html.Span([html.Br(style={"line-height": "40"})]),
    
    dash_table.DataTable(
        id='data-table', 
        style_data={"text-align": "left", "width": "1500px", "height": "50px"},
        style_header={'backgroundColor':"#a2d2ff", "text-align": "left", "fontSize":"20px", "font-weight":'bold'},
        )


], style={"text-align" : "center"})
# style={"text-align: center;"}
# style={"width": "100px", "height": "40px", "fontSize": "20px"},
@app.callback(
    [Output('graph', 'figure'),
    Output("category-dropdown2", 'options'),
    Output('data-table', 'data'),],
    [Input("update-button", "n_clicks")],
    [
        State('score-slider', 'value'),
        State("checklist", "value"),
        State("radioItems", "value"),
        # State("noun_counts_min", 'value'),
        State("noun_counts_max", 'value'),
        State("category-dropdown2", 'value'),
        State("column_list", 'value'),
        # State("words_dropdown", 'value')
    ],
    )

def update_figure(n_clicks, selected_scores, select_sentiment, fileter_col, noun_counts_max, dropdown_option, column_list):
    print("Filter Column:", fileter_col)
    filter_df = senti_df.query(f"(`{fileter_col}` >= {selected_scores[0]}) and (`{fileter_col}` < {selected_scores[1]})")
    filter_df = filter_df[filter_df['결과'].isin(select_sentiment)]
    # filter_df.reset_index(drop=True, inplace=True)

    # 명사 추출 부분
    for i in filter_df.index:
        filter_df['명사'][i] = eval(filter_df['명사'][i])

    filter_noun_list = []
    for i in filter_df.index:
        for j in filter_df['명사'][i]:
            filter_noun_list.append(j)
    

    # 명사 count 부분        
    filter_count = Counter(filter_noun_list)
    filter_most_common = filter_count.most_common()

    count_value = filter_most_common[0:noun_counts_max]

    words_value = [value_[0] for value_ in count_value]
    count_word = [value_[1] for value_ in count_value]

    # # plotly 버전
    global view_df
    
    view_df = pd.DataFrame(columns=['단어', '빈도수', 'Color'])
    view_df['단어'] = words_value
    view_df['빈도수'] = count_word
    
    words_list = view_df['단어'].unique().tolist()
    
    top_30 = round(len(view_df) * 0.3)
    
    view_df['Color'] = ['상위30' if i < top_30 else '하위30' if i >= len(view_df) - top_30 else '중간' for i in range(len(view_df))]
    
    fig = px.bar(view_df, x='단어', y='빈도수', color='Color', title='단어 빈도수 막대 그래프',
                 color_discrete_map={'상위30': '#1565c0', '중간': '#2196f3', '하위30': '#bbdefb'})
    
    # table_df = filter_df[filter_df['명사'].astype(str).str.contains(f'{dropdown_option}')][[column_list]]
    mask = [i for i in filter_df.index if dropdown_option in filter_df.loc[i, '명사']]
    table_df = filter_df.loc[mask][column_list].reset_index(drop=True)
    table_df.to_excel('./data/now_view.xlsx', index=False)
    table_view = table_df.to_dict('records')
    
    return fig, words_list, table_view

@app.callback(
    Output("download-text-index", "data"),
    Input("btn_txt", "n_clicks"),
    )

def download_dataframe(n_clicks2):
    if n_clicks2 is None:
        return None
    else:
        return dcc.send_file('./data/now_view.xlsx')


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=9000)
