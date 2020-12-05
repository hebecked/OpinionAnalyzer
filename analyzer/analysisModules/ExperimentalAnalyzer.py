"""
TODO:

- test and install various libs
- Reduce article(s) to a few representative words (Top N=8(?) words in (maximum word frequency - common words)) (ML-NLP approaches, gpt summary?)
- Run sentiment analysis on comments
- Compare different sentiment analyser and possibly combine to a ensemble approach to increase accuracy and obtain reasonable errors
- Find additional analyser to run (5 personality traits, mood, IQ/education, wordcount vs sentiment, spelling, offensiveLanguage detection, ...)
"""
#from flair.models import TextClassifier
#from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from textblob_de import TextBlobDE as TextBlob
from scipy.special import softmax
#import tensorflow as tf
import numpy as np
import json


class multiling_bert_sentiment: 

	def __init__(self):
		#Based on Amazonreview (1-5 stars)		#https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment?text=Nicht+kaufen 			
		self.tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
		self.model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
	
	def analyze(self,text):
		inputs = self.tokenizer(text, return_tensors="pt")
		proOrCon = self.model(**inputs)
		weights=proOrCon[0].detach().numpy()[0]
		weights=softmax(weights)
		average=np.average(np.linspace(1,5,5),weights=weights)
		error=np.sqrt(np.average((np.linspace(1,5,5)-average)**2,weights=weights))*2./5.
		average=average*2./5.-1
		return [average,error]

class german_bert_sentiment: 

	def __init__(self):
		#Based on a range of sources including twitter, facebook, product reviews #https://huggingface.co/oliverguhr/german-sentiment-bert?text=Du+Arsch%21
		self.tokenizer = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")
		self.model = AutoModelForSequenceClassification.from_pretrained("oliverguhr/german-sentiment-bert")
	
	def analyze(self,text):
		inputs = self.tokenizer(text, return_tensors="pt")
		proOrCon = self.model(**inputs)
		weights=proOrCon[0].detach().numpy()[0]
		weights[2], weights[1] = weights[1], weights[2]
		weights=softmax(weights)
		average=np.average(np.linspace(1,-1,3),weights=weights)
		error=np.sqrt(np.average((np.linspace(1,-1,3)-average)**2,weights=weights))
		return [average,error]

class Textblob_sentiment: 

	#More information at https://textblob-de.readthedocs.io/en/latest/
	def __init__(self):
		pass
		
	def analyze(self,text):
		blob = TextBlob(text)
		mood = blob.sentiment
		return mood.polarity

	def abalyzeSubjectivity(self,text):
		blob = TextBlob(text)
		mood = blob.sentiment
		return mood.subjectivity


#classifier = TextClassifier.load('de-offensive-language') # en-sentiment

with open('../Testdata/TestArticle.json') as f:
	testArticle = json.load(f)
#dict_keys(['url', 'id', 'channel', 'subchannel', 'headline', 'intro', 'text', 'topics', 'author', 'comments_enabled', 'date_created', 'date_modified', 'date_published', 'breadcrumbs'])


with open('../Testdata/TestComments.json') as f:
	testComments = json.load(f)

#print(testArticle)
#print(testComments)
results=["positiv", "negativ", "neutral"]

#Based on Amazonreview (1-5 stars)	
SentimentModel1=multiling_bert_sentiment()

#Based on a range of sources including twitter, facebook, product reviews
SentimentModel2=german_bert_sentiment()

testText="Du Arsch!" 


result1=SentimentModel1.analyze(testText)
result2=SentimentModel2.analyze(testText)
result3=Textblob_sentiment().analyze(testText)
results=np.array([result1, result2])
finalResult=np.average(results.T[0], weights=1/results.T[1]**2)
finalError=np.sqrt(1/np.mean(1/results.T[1]**2))
print("Test: ", result1 , result2, result3, finalResult, finalError)


i=0
for comment in testComments:
	if comment["user"] is not None and comment["body"] is not None:
		#sentence = Sentence(comment["body"])
		#Tourette = classifier.predict(sentence)

		

		result1=SentimentModel1.analyze(comment["body"])
		result2=SentimentModel2.analyze(comment["body"])
		result3=Textblob_sentiment().analyze(comment["body"])
		results=np.array([result1, result2])
		finalResult=np.average(results.T[0], weights=1/results.T[1]**2)
		finalError=np.sqrt(1/np.mean(1/results.T[1]**2))
		print(result1 , result2, result3, finalResult, finalError)

	i+=1
