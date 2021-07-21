FROM python:3.8.9

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
