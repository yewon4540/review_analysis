import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import ast
from collections import defaultdict
import re
import networkx as nx
import plotly.graph_objects as go
from string import printable

data = pd.read_csv('./data/senti_df.csv',sep="\t")
data['명사'] = data['명사'].apply(ast.literal_eval)


def process_data(data, selected_scores, select_sentiment, filter_col, noun_counts_max):
    # 데이터 필터링
    filter_df = data.query(f"(`{filter_col}` >= {selected_scores[0]}) and (`{filter_col}` < {selected_scores[1]})")
    filter_df = filter_df[filter_df['결과'].isin(select_sentiment)]

    # 명사 컬럼 처리: 문자열이면 ast.literal_eval로 평가하고, 그렇지 않으면 그대로 사용
    filter_df['명사'] = filter_df['명사'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # 명사 count
    return count_nouns(filter_df['명사'], noun_counts_max)

def count_nouns(nouns, noun_counts_max):
    # 명사 리스트 확장 및 카운트, 2글자 이상인 명사만 포함
    noun_list = [noun for sublist in nouns for noun in sublist if len(noun) >= 2]
    count = Counter(noun_list)
    return count.most_common(noun_counts_max)


def create_dataframe(word_counts):
    # 데이터 구조가 올바른지 검사하는 로직 추가
    if not all(isinstance(w, tuple) and len(w) == 2 for w in word_counts):
        raise ValueError("word_counts must be a list of tuples (word, count)")

    words = [w[0] for w in word_counts]
    counts = [w[1] for w in word_counts]
    
    df = pd.DataFrame({'단어': words, '빈도수': counts})
    top_30 = round(len(df) * 0.3)
    df['Color'] = ['상위30' if i < top_30 else '하위30' if i >= len(df) - top_30 else '중간' for i in range(len(df))]
    return df

def create_bar_graph(df):
    # 막대 그래프 생성
    fig = px.bar(df, x='단어', y='빈도수', color='Color', title='단어 빈도수 막대 그래프',
                 color_discrete_map={'상위30': '#1565c0', '중간': '#2196f3', '하위30': '#bbdefb'})
    return fig


# 사용 예
def update_figure(selected_scores, select_sentiment, filter_col, noun_counts_max):
    word_counts = process_data(data, selected_scores, select_sentiment, filter_col, noun_counts_max)
    print("Generated word_counts:", word_counts)  # 데이터 확인 로그
    return word_counts


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
                            height=600, width=700, template="plotly_white"))
    return fig


def extract_top_keywords(data, filter_col, select_sentiment, selected_scores, noun_counts_max=10):
    # 데이터 필터링
    query = f"(`{filter_col}` >= {selected_scores[0]}) and (`{filter_col}` <= {selected_scores[1]})"
    filter_df = data.query(query)
    filter_df = filter_df[filter_df['결과'].isin(select_sentiment)]

    # 명사 컬럼 처리
    filter_df['명사'] = filter_df['명사'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # 명사 count
    noun_list = [noun for sublist in filter_df['명사'] for noun in sublist if len(noun) >= 2]
    count = Counter(noun_list)
    top_keywords = [word for word, _ in count.most_common(noun_counts_max)]

    return top_keywords



def clean_excel_string(s):
    # Excel에서 허용하지 않는 문자를 제거합니다.
    return ''.join(filter(lambda x: x in printable, s))

def save_to_excel(df, filepath='exported_data.xlsx'):
    # 모든 문자열 컬럼에 대해 clean_excel_string 함수 적용
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].apply(clean_excel_string)
    
    # 데이터프레임을 엑셀로 저장
    df.to_excel(filepath, index=False)
    return filepath
