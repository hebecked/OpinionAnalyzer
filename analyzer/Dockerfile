#Inspired by https://github.com/poteha/docker-nlp/
FROM python:3.7-slim-buster


RUN apt-get update && apt-get install -y cron

RUN pip install torch==1.7.0+cpu torchvision==0.8.1+cpu torchaudio==0.7.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install flair==0.6.1
RUN pip install	psycopg2-binary==2.8.6

# For deployment the used models should be preloaded
#RUN python -c 'import flair; _ = flair.models.SequenceTagger.load("ner-fast")'

WORKDIR /usr/src/analyzer
COPY ./src .

CMD [ "cron", "-f"]


#Alternative Python packages for NLP:
#    spacy==2.0.11
#    dateparser==0.7.0 \
#    pymorphy2==0.8 \
#    yargy==0.11.0 \
#    natasha==0.10.0 \
#    nltk==3.2.1 \
#    yake==0.3.7 \
#    python-dateutil==2.7.5