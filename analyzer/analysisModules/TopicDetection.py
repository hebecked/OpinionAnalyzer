
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
import nltk
from HanTa import HanoverTagger as ht
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







class Word2Vector:
	import gensim

	def __init__(self):
		#source: https://devmount.github.io/GermanWordEmbeddings/ (http://cloud.devmount.de/d2bc5672c523b086) https://cloud.devmount.de/d2bc5672c523b086/german.model
		#problem with words not in the model, requires the use of preprocessing.py functions.
		self.model = gensim.models.KeyedVectors.load_word2vec_format("../Testdata/german_word2vec.model", binary=True) 
		#Alternative is FastText in other file 



tagger = ht.HanoverTagger('morphmodel_ger.pgz')


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
		tokenized_sent = nltk.tokenize.word_tokenize(row[1], language='german')
		if len(tokenized_sent) == 0:
			commonGerWords.append("")
			continue
		word = tagger.tag_sent(tokenized_sent)[0][1]
		word = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', word).lower()
		commonGerWords.append(word)
		word2 = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', row[1]).lower()
		if word != word2:
			commonGerWords.append(word2)

wordlist = testArticle["text"].split()


wordfreq = dict()
for word in wordlist:
	#clean up the strings from punctuations
	tokenized_sent = nltk.tokenize.word_tokenize(word, language='german')
	word = tagger.tag_sent(tokenized_sent)[0][1]
	word = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', word).lower() #remove numbers?


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
