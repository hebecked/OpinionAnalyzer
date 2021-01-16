
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
		other_stopwords = set(nltk.corpus.stopwords.words("german"))
		if __name__ == "__main__": #TODO move file readin to private sub-function
			stop_word_path = '../Testdata/CommonGerWords.csv'
		else:
			stop_word_path = './Testdata/CommonGerWords.csv'
		with open(stop_word_path, newline='') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			#skip first 2 lines
			spamreader.__next__()
			spamreader.__next__()
			for row in spamreader:
				tokenized_sent = nltk.tokenize.word_tokenize(row[1], language='german')
				if len(tokenized_sent) == 0:
					self.commonGerWords.append("")
					continue
				word = self.tagger.tag_sent(tokenized_sent)[0][1]
				word = re.sub('[^A-Za-züäößÄÖÜ]+', '', word).lower() #if needed ad numbers 0-9
				self.commonGerWords.append(word) # add lemmatized string
				word2 = re.sub('[^A-Za-züäößÄÖÜ]+', '', row[1]).lower()
				if word != word2:
					self.commonGerWords.append(word2) # Add unformated string if not identical
		for word in other_stopwords:
			if word not in self.commonGerWords:
				self.commonGerWords.append(word) #add additional stopwords from lib
		self.commonGerWords = set(self.commonGerWords)


	def get_wordfrequency(self, article: str) -> dict:
		"""
		Extract the most frequent words from an article body.

		:param str article: The article body
		:return: Topics determined from the article body.
		:rtype: dict[str: int]
		"""
		wordlist = article.split()
		wordfreq = dict()
		for word in wordlist:
			#clean up the strings from punctuations
			tokenized_sent = nltk.tokenize.word_tokenize(word, language='german')
			word = self.tagger.tag_sent(tokenized_sent)[0][1]
			#if desired all non-nouns can be removed here
			word = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', word).lower() #remove numbers?
			# Check if the word is already in the dictionary 
			if word in wordfreq.keys():  
			    wordfreq[word] = wordfreq[word] + 1
			else:
			    wordfreq[word] = 1
		return wordfreq
		

	def get_topics(self, article: str) -> list:
		"""
		Extract topics from an article body.
		Hint: It is recommended to attach the headline to the body.

		:param str article: The article body
		:return: Topics determined from the article body.
		:rtype: list[str]
		"""

		wordfreq = self.get_wordfrequency(article)

		# remove common German words
		for commonWord in (set(wordfreq.keys()) & self.commonGerWords):
			del wordfreq[commonWord]

		#sort and return
		#print(sorted(wordfreq.items(), key=lambda item: item[1]))	# uncomment for debugging
		result=[]
		while len(result) < 5 and len(wordfreq) > 0:
			topic=max(wordfreq.items(), key=lambda item: item[1])
			if topic[1]<=2:
				break
			result.append(topic[0])
			del wordfreq[topic[0]]

		#possibly reduce to nouns in the future
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