#Inspired by https://github.com/poteha/docker-nlp/
FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y cron

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# For deployment the used models should be preloaded
#RUN python -c 'import flair; _ = flair.models.SequenceTagger.load("ner-fast")'

WORKDIR /usr/src/analyzer
COPY ./src .

CMD [ "cron", "-f"]
