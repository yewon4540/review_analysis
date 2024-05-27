import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages
import ast
from graph import update_figure, create_dataframe, create_bar_graph, build_context_freq, create_network_graph,extract_top_keywords,data  # 필요한 함수 임포트
from string import printable
show_pages(
    [
        Page("home.py", "메인페이지", "🏠"),
        Page("bar_page.py", "빈도 그래프",  "🧰"),

    ]
)

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
def main():
    st.title('Bar Graph Page')

    # 세션 상태 초기화
    if 'graph' not in st.session_state:
        st.session_state.graph = None
        st.session_state.graph_type = None

    # 입력 설정
    selected_scores = st.slider('점수 범위 선택', 0, 100, (45, 75))
    select_sentiment = st.selectbox('감정 선택', ['긍정', '부정', '중립'])
    filter_col = st.selectbox('필터할 컬럼 선택', ['과정종합점수', '감정 점수'])
    noun_counts_max = st.number_input('최대 명사 수', min_value=1, max_value=100, value=10)

    # 바 그래프 생성
    if st.button('바 그래프 생성'):
        word_counts = update_figure(selected_scores, [select_sentiment], filter_col, noun_counts_max)
        df = create_dataframe(word_counts)
        fig = create_bar_graph(df)
        st.session_state.graph = fig
        st.session_state.graph_type = 'bar'

    if st.session_state.graph is not None:
        if st.session_state.graph_type == 'bar':
            st.plotly_chart(st.session_state.graph)

    # 네트워크 그래프 생성
    target_word = st.text_input("키워드를 입력하세요 ", "과정")
    window_size = st.number_input("키워드 범위", min_value=1, max_value=5, value=1)
    top_n = st.number_input("키워드 출력 개수", min_value=1, max_value=50, value=20)
    if st.button('네트워크 그래프 생성'):
        noun_lists = data['명사'].tolist()
        context_freq = build_context_freq(noun_lists, target_word, window_size)
        fig = create_network_graph(context_freq, target_word, top_n)
        st.session_state.graph = fig
        st.session_state.graph_type = 'network'

    # 조건에 따라 그래프 표시
    if st.session_state.graph is not None:
        if st.session_state.graph_type == 'network':
            st.plotly_chart(st.session_state.graph)

    # 상위 키워드 추출 및 표시
    top_keywords = extract_top_keywords(data, filter_col, [select_sentiment], selected_scores)
    selected_keyword = st.selectbox("Select a keyword from the top frequent words:", top_keywords)

    # 데이터 테이블 표시
    
    selected_columns = st.multiselect("Choose which columns to display:", ['검색어','훈련명','훈련기관','과정종합점수','문장', '결과'])
    if selected_keyword and selected_columns:
        filtered_data = data[data['명사'].apply(lambda x: selected_keyword in ast.literal_eval(x) if isinstance(x, str) else selected_keyword in x)]
        if not filtered_data.empty:
            st.dataframe(filtered_data[selected_columns])
        else:
            st.write("키워드를 찾을 수 없습니다.")
    
    if st.button('엑셀로 저장하기'):
        
        filepath = save_to_excel(data)
        st.success(f' 엑셀로 저장되었습니다! {filepath}')
if __name__ == '__main__':
    main()

