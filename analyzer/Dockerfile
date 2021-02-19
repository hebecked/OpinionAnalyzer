# Inspired by https://github.com/poteha/docker-nlp/
FROM python:3.8-slim-buster

# Set root as default usr
USER root

# Update compiler
RUN apt-get update
RUN apt-get install -y g++
# gcc cpp glibc-devel glibc-headers kernel-headers libmpc libstdc++-devel mpfr 

# Set the working directory in the container
WORKDIR /usr/src/app

# Set pythonpath env variable for better module identification
ENV PYTHONPATH='/usr/src/app/'

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Just generically copy everything to avoid conflicts later when adding new moduls
COPY . .

#load required models for nlp (reduces startup time)
COPY loadRequiredModels.py .
RUN python3 -m textblob.download_corpora
RUN python3 loadRequiredModels.py
#RUN python3 -m spacy download de

# Run on init
CMD ["python3","-u", "index.py"]
