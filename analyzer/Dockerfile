# Inspired by https://github.com/poteha/docker-nlp/
FROM python:3.8-slim-buster

# Set root as default usr
USER root

# Set the working directory in the container
WORKDIR /usr/src/app

# Set pythonpath env variable for better module identification
ENV PYTHONPATH='/usr/src/app/'

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m textblob.download_corpora
#RUN python3 -m spacy download de

# Just generically copy everything to avoid conflicts later when adding new moduls
COPY . .

# Run on init
CMD ["python3","-u", "index.py"]
