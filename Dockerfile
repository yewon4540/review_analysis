# 후기데이터 Dashboard
FROM python:3.10

RUN apt-get update

RUN rm -rf /var/lib/apt/lists/*

RUN python3 -m pip --no-cache-dir install --upgrade "pip<20.3" setuptools

RUN apt-get install -y python3

ENV TZ=Asia/Seoul
RUN apt-get update && \
    apt-get install -y tzdata

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y sudo

WORKDIR /home

# COPY requirements_dash.txt /home
COPY ../. .
RUN pip install --upgrade pip
RUN pip install -r /home/requirements_dash.txt

# CMD ["python3", "main.py"]
ENTRYPOINT ["python3", "main.py"]