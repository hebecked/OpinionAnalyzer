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

					
tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")


i=0
for comment in testComments:
	if comment["user"] is not None and comment["body"] is not None:
		sentence = Sentence(comment["body"])
		#tokenized_text = tokenizer.tokenize(comment["body"])
		#token_ids = tokenizer.convert_tokens_to_ids(tokenized_text)
		#token_ids2 = tokenizer.encode(comment["body"])
		Tourette = classifier.predict(sentence)
		inputs = tokenizer(comment["body"], return_tensors="pt")
		proOrCon = model(**inputs)
		print("\n" + comment["body"])
		print(str(i) + ": " + comment["user"]["username"] + \
			" Text length: " + str(len(comment["body"])) + \
			" subcomments: " + str(len(comment["replies"])) + \
			" Swearing: " + str(Tourette) + \
			" Sentiment (star): " + str(1+proOrCon[0].argmax()) )  #Mache ich heir das richtige?
	i+=1