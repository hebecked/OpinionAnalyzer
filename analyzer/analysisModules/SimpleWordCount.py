
#from flair.models import TextClassifier
#from flair.data import Sentence
#from transformers import AutoTokenizer, AutoModelForSequenceClassification
#from textblob_de import TextBlobDE as TextBlob
#from scipy.special import softmax
#import tensorflow as tf
import numpy as np
import json
import string
import re
import csv
#import spacy
#nlp = spacy.load('de')


#throws errors
#Usage: 	tags = tagger.tag_text(word,tagonly=True)
#			pprint.pprint(tags)
#import treetaggerwrapper
#tagger = treetaggerwrapper.TreeTagger(TAGLANG='de')


#requires setup of a mongo db :(  (Usage:print(gn.lemmatise(word)))
#from pygermanet import load_germanet
#gn = load_germanet()


with open('../Testdata/TestArticle.json') as f:
	testArticle = json.load(f)
#dict_keys(['url', 'id', 'channel', 'subchannel', 'headline', 'intro', 'text', 'topics', 'author', 'comments_enabled', 'date_created', 'date_modified', 'date_published', 'breadcrumbs'])


with open('../Testdata/TestComments.json') as f:
	testComments = json.load(f)

commonGerWords=[]
with open('../Testdata/CommonGerWords.csv', newline='') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',')
	#skip first 2 lines
	spamreader.__next__()
	spamreader.__next__()
	for row in spamreader:
		commonGerWords.append(re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', row[1]).lower())

wordlist = testArticle["text"].split()


wordfreq = dict()
for word in wordlist:
	#clean up the strings from punctuations
	word=re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', word).lower() #remove numbers?

	# Check if the word is already in dictionary 
	if word in wordfreq:  
	    wordfreq[word] = wordfreq[word] + 1
	else:
	    wordfreq[word] = 1

# remove common German words
for commonWord in commonGerWords:
	if commonWord in wordfreq.keys():
		del wordfreq[commonWord]

#sort and print
print(sorted(wordfreq.items(), key=lambda item: item[1]))
result=[]
while len(result) < 5 or len(wordfreq) <=0:
	topic=max(wordfreq.items(), key=lambda item: item[1])
	if topic[1]<=2:
		break
	result.append(topic[0])
	del wordfreq[topic[0]]


print(result)
