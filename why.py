import dash
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import networkx as nx
from collections import Counter, defaultdict
import pandas as pd
import plotly.express as px
import ast
import re

# 데이터 불러오기 및 전처리
senti_df = pd.read_csv('./data/senti_df.csv', sep="\t")
senti_df['명사'] = senti_df['명사'].apply(ast.literal_eval)

# 명사를 기반으로 문맥 빈도 수를 계산하는 함수
def build_context_freq(noun_lists, target_noun, window_size=1):
    context_freq = defaultdict(int)
    for nouns in noun_lists:
        cleaned_nouns = [re.sub(r'[^\w]', '', noun) for noun in nouns if len(re.sub(r'[^\w]', '', noun)) >= 2]
        if target_noun in cleaned_nouns:
            idx = cleaned_nouns.index(target_noun)
            start = max(idx - window_size, 0)
            end = min(idx + window_size + 1, len(cleaned_nouns))
            for i in range(start, end):
                if i != idx:
                    context_freq[cleaned_nouns[i]] += 1
    return context_freq

# 네트워크 그래프를 생성하는 함수
def create_network_graph(context_freq, target_word, top_n=20):
    top_words = sorted(context_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    G = nx.Graph()
    G.add_node(target_word, size=20)
    G.nodes[target_word]['text'] = f'{target_word}: Central node'
    for word, freq in top_words:
        G.add_node(word, size=freq * 10)
        G.add_edge(target_word, word, weight=freq)
        G.nodes[word]['text'] = f'{word}: Count: {freq}'
    pos = nx.spring_layout(G)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]['text'])
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text, textposition="top center", hoverinfo='text',
                            marker=dict(showscale=True, colorscale='YlGnBu', color=[10, 15, 10], size=10, line_width=2))
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(showlegend=False, hovermode='closest',
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), margin=dict(b=20, t=20, l=20, r=20),
                            height=600, width=1960, template="plotly_white"))
    return fig

app = Dash(__name__)
app.layout = html.Div([
    html.H4('HRD-net 후기 데이터'),
    dcc.Graph(id='network-graph'),
    dcc.Input(id='target-word-input', type='text', value='과정', placeholder='Enter a target word...'),
    html.Button('Submit', id='network-button', n_clicks=0),
    html.A("돌아가기", href="http://10.40.1.109:9000/", style={"fontSize": "20px", "margin": "10px"}),
])


@app.callback(
    Output('network-graph', 'figure'),
    [Input('network-button', 'n_clicks')],
    [State('target-word-input', 'value')]
)
def update_graph(n_clicks, target_word):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    noun_lists = senti_df['명사'].tolist()
    context_freq = build_context_freq(noun_lists, target_word)
    fig = create_network_graph(context_freq, target_word)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=9091)
