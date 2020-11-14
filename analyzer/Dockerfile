#Inspired by https://github.com/poteha/docker-nlp/blob/master/Dockerfile.cpu
FROM python:3.9-slim

RUN apt-get update && apt-get install -y gcc g++

RUN pip install torch==1.7.0
RUN pip install flair==0.6.1
#RUN pip install spacy==2.0.11

RUN pip install \
	numpy==1.19.2 \
	matplotlib==3.3.2 \
	psycopg2==2.8.6
#    dateparser==0.7.0 \
#    pymorphy2==0.8 \
#    yargy==0.11.0 \
#    natasha==0.10.0 \
#    nltk==3.2.1 \
#    yake==0.3.7 \
#    python-dateutil==2.7.5

#RUN python -m nltk.downloader stopwords && python -m nltk.downloader punkt  && \
#    python -m nltk.downloader averaged_perceptron_tagger

#RUN python -c 'import flair; _ = flair.models.SequenceTagger.load("ner-fast")'

WORKDIR /usr/src/analyzer
COPY ./src .

#CMD [ "npm", "start" ]