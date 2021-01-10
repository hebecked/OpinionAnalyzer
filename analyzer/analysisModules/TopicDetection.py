
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


class baseline_topic_detection:


	def __init__(self):
		self.tagger = ht.HanoverTagger('morphmodel_ger.pgz')
		self.commonGerWords=[]
		with open('../Testdata/CommonGerWords.csv', newline='') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			#skip first 2 lines
			spamreader.__next__()
			spamreader.__next__()
			for row in spamreader:
				self.commonGerWords.append(re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', row[1]).lower())
				tokenized_sent = nltk.tokenize.word_tokenize(row[1], language='german')
				if len(tokenized_sent) == 0:
					self.commonGerWords.append("")
					continue
				word = self.tagger.tag_sent(tokenized_sent)[0][1]
				word = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', word).lower()
				self.commonGerWords.append(word)
				word2 = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', row[1]).lower()
				if word != word2:
					self.commonGerWords.append(word2)


		

	def get_topics(self, article):
		'''
		Extract topics from an article body.
		Hint: It is recommended to attach the headline to the body.

		:param str article: The article body
		:return: Topics determined from the article body.
		:rtype: list[str]
		:raises ValueError: if the message_body exceeds 160 characters
		:raises TypeError: if the message_body is not a basestring
		'''
		wordlist = article.split()
		wordfreq = dict()
		for word in wordlist:
			#clean up the strings from punctuations
			tokenized_sent = nltk.tokenize.word_tokenize(word, language='german')
			word = self.tagger.tag_sent(tokenized_sent)[0][1]
			word = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', word).lower() #remove numbers?
			# Check if the word is already in the dictionary 
			if word in wordfreq:  
			    wordfreq[word] = wordfreq[word] + 1
			else:
			    wordfreq[word] = 1

		# remove common German words
		for commonWord in self.commonGerWords:
			if commonWord in wordfreq.keys():
				del wordfreq[commonWord]
		
		#sort and return
		#print(sorted(wordfreq.items(), key=lambda item: item[1]))	# uncomment for debugging
		result=[]
		while len(result) < 5 or len(wordfreq) <=0:
			topic=max(wordfreq.items(), key=lambda item: item[1])
			if topic[1]<=2:
				break
			result.append(topic[0])
			del wordfreq[topic[0]]

		return result


if __name__ == "__main__":

	with open('../Testdata/TestArticle.json') as f:
		testArticle = json.load(f)
		#dict_keys(['url', 'id', 'channel', 'subchannel', 'headline', 'intro', 'text', 'topics', 'author', 'comments_enabled', 'date_created', 'date_modified', 'date_published', 'breadcrumbs'])

	with open('../Testdata/TestComments.json') as f:
		testComments = json.load(f)

	#run a testArticle
	print("Running a topic detection test...")
	bltd = baseline_topic_detection()
	results = bltd.get_topics( testArticle["text"] )
	print( results )
	print("Test ran successfully.")