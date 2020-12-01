"""
TODO:

- test and install various libs
- Reduce article(s) to a few representative words (Top N=8(?) words in (maximum word frequency - common words)) (ML-NLP approaches, gpt summary?)
- Run sentiment analysis on comments
- Compare different sentiment analyser and possibly combine to a ensemble approach to increase accuracy and obtain reasonable errors
- Find additional analyser to run (5 personality traits, mood, IQ/education, wordcount vs sentiment, spelling, offensiveLanguage detection, ...)
"""
from flair.models import TextClassifier
from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from textblob_de import TextBlobDE as TextBlob
import tensorflow as tf
import numpy as np
import json

classifier = TextClassifier.load('de-offensive-language') # en-sentiment

with open('../Testdata/TestArticle.json') as f:
	testArticle = json.load(f)
#dict_keys(['url', 'id', 'channel', 'subchannel', 'headline', 'intro', 'text', 'topics', 'author', 'comments_enabled', 'date_created', 'date_modified', 'date_published', 'breadcrumbs'])


with open('../Testdata/TestComments.json') as f:
	testComments = json.load(f)

#print(testArticle)
#print(testComments)
results=["positiv", "negativ", "neutral"]

#Based on Amazonreview (1-5 stars)					
tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
#Based on a range of sources including twitter, facebook, product reviews
tokenizer2 = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")
model2 = AutoModelForSequenceClassification.from_pretrained("oliverguhr/german-sentiment-bert")

correlationMatrix=[[0]*3 for i in range(5)]

i=0
for comment in testComments:
	if comment["user"] is not None and comment["body"] is not None:
		sentence = Sentence(comment["body"])
		Tourette = classifier.predict(sentence)
		inputs = tokenizer(comment["body"], return_tensors="pt")
		proOrCon = model(**inputs)
		inputs2 = tokenizer2(comment["body"], return_tensors="pt")
		proOrCon2 = model2(**inputs2)
		blob = TextBlob(comment["body"])
		mood = blob.sentiment
		print( proOrCon, proOrCon2, mood )
		#print("\n" + comment["user"]["username"] + ": " + comment["body"])
		#print(str(i) + ": " +  \
		#	" Text length: " + str(len(comment["body"])) + \
		#	"; subcomments: " + str(len(comment["replies"])) + \
		#	"; Swearing: " + str(Tourette) + \
		#	"; Sentiment (star): " + str(1+proOrCon[0].argmax().tolist()) + "/" + results[proOrCon2[0][0].argmax()] )  #Mache ich heir das richtige?
		stars=proOrCon[0].argmax().tolist()
		rating=proOrCon2[0][0].argmax().tolist()
		correlationMatrix[stars][rating]+=1
	i+=1
	#if i == 10:
	#	break
for i in range(5):
	print(correlationMatrix[i])