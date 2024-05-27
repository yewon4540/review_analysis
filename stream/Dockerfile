# 기본 이미지로 Python 3.8-slim을 사용
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지와 라이브러리 설치
RUN pip install --upgrade pip
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# 애플리케이션 파일 복사
COPY . /app

# Streamlit 포트 설정
EXPOSE 8501

# Streamlit 애플리케이션 실행 명령
CMD ["streamlit", "run", "home.py"]