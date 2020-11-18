FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y cron

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt


WORKDIR /usr/src/scraper
COPY ./src .

CMD [ "cron", "-f"]
