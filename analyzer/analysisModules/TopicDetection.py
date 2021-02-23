
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
import fasttext
import fasttext.util
from scipy import spatial 
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
	"""
	A primitive topic detection based on word frequency.
	Stop words and other common words are removed and the most frequent words are selected. 
	"""


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


class mean_distance_topic_detection(baseline_topic_detection):

	def __init__(self):
		super().__init__()
		self.ft = fasttext.load_model('../Testdata/cc.de.50.bin')

	def _get_ft_vectors(self, text):
		words_n_vectors=[]
		words = re.split('\s+', text)
		for word in words:
			clean_word = re.sub('[^A-Za-züäößÄÖÜ]+', '', word)
			ft_word = self.ft.get_word_vector(clean_word)
			words_n_vectors.append([clean_word,ft_word])
		return words_n_vectors

	def get_topics(self, text):
		wnv = self._get_ft_vectors(text)
		wnv_t = list(zip(*wnv))
		doc_vec = np.mean(wnv_t[1], axis=0)
		max_dist = 0
		max_index = 0
		results = dict()
		for i, word_vec in enumerate(wnv):
			distance = spatial.distance.cosine(word_vec[1],doc_vec)
			results[word_vec[0]] = distance
			if distance > max_dist:
				max_dist = distance
				max_index = i
		print( wnv[max_index][0] )
		return dict(sorted(results.items(), key=lambda item: item[1]))






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

	mdtp = mean_distance_topic_detection()
	sorted_topics = mdtp.get_topics(testArticle["text"])
	print(sorted_topics)