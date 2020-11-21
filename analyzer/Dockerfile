#Inspired by https://github.com/poteha/docker-nlp/
FROM python:3.7-slim-buster

USER root

# set the working directory in the container
WORKDIR /usr/src/app

#RUN apt-get update && apt-get install -y nano
#Not necessary yet, maybe we can also better use a python module for that which would make it more generic
#RUN apt-get update && apt-get install -y cron

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# For deployment the used models should be preloaded -- Martin: Why? Why not just load them when they are executed
#RUN python -c 'import flair; _ = flair.models.SequenceTagger.load("ner-fast")'

#Just generically copy everything to avoid conflicts later when adding new moduls
COPY . .

#Run on init
CMD ["python3","-u", "index.py"]
