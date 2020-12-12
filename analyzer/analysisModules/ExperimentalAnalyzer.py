"""
TODO:

1. Clean up Testfile and split over different files (1 for each lib class + 1 analyzing comments +1 analyzing articles)
2. Libs to add: Topic detection, big 5 personality traits, IQ/Education, origin, wordcount, spelling, offensiveLanguage detection, mood
Sources:
Prep text (bag of words): 	https://monkeylearn.com/topic-analysis/
							https://towardsdatascience.com/nlp-extracting-the-main-topics-from-your-dataset-using-lda-in-minutes-21486f5aa925
Get text topic:	https://spacy.io/models/de
				Reduce article(s) to a few representative words (Top N=8(?) words in (maximum word frequency - common words)) 
				(ML-NLP approaches, gpt summary?)
Get Personalities: 	https://github.com/jkwieser/personality-detection-text
					https://github.com/SenticNet/personality-detection
"""



#from flair.models import TextClassifier
#from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from textblob_de import TextBlobDE as TextBlob
from scipy.special import softmax
#import tensorflow as tf
import numpy as np
import json


class multilang_bert_sentiment: 

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

	#More information at https://textblob-de.readthedocs.io/en/latest/ and https://github.com/sloria/TextBlob/
	#https://machine-learning-blog.de/2019/06/03/stimmungsanalyse-sentiment-analysis-auf-deutsch-mit-python/
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

#Based on Amazonreview (1-5 stars)	
SentimentModel1=multilang_bert_sentiment()

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
