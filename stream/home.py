import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages
from streamlit_lottie import st_lottie
import requests
show_pages(
    [
        Page("home.py", "메인페이지", "🏠"),
        Page("bar_page.py", "빈도 그래프",  "🧰"),

    ]
)
def load_lottieurl(url):
    """Lottie URL로부터 JSON 데이터를 로드합니다."""
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None

def main():
    lottie_url = 'https://assets5.lottiefiles.com/packages/lf20_V9t630.json'
    lottie_json = load_lottieurl(lottie_url)

    if lottie_json:
        st_lottie(lottie_json, width= 800, height=600, key="initial")

if __name__ == '__main__':
    main()
