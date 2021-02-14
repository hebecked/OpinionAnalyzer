import numpy as np
import json
import string
import re
import csv
import nltk
from HanTa import HanoverTagger as HT
from flair.data import Sentence
from flair.models import SequenceTagger


class BaselineTopicDetection:

	def __init__(self, use_flair: bool = False):
		self.tagger = HT.HanoverTagger('morphmodel_ger.pgz')
		self.use_flair = False
		if use_flair:
			self.flair_tagger = SequenceTagger.load('de-ner')
			self.use_flair = True
		self.commonGerWords = []
		other_stopwords = set(nltk.corpus.stopwords.words("german"))
		if __name__ == "__main__": #TODO move file readin to private sub-function
			stop_word_path = '../Testdata/CommonGerWords.csv'
		else:
			stop_word_path = './Testdata/CommonGerWords.csv'
		with open(stop_word_path, newline='') as csvfile:
			spam_reader = csv.reader(csvfile, delimiter=',')
			# skip first 2 lines
			spam_reader.__next__()
			spam_reader.__next__()
			for row in spam_reader:
				tokenized_sent = nltk.tokenize.word_tokenize(row[1], language='german')
				if len(tokenized_sent) == 0:
					self.commonGerWords.append("")
					continue
				word = self.tagger.tag_sent(tokenized_sent)[0][1]
				word = re.sub('[^A-Za-züäößÄÖÜ]+', '', word).lower()  # if needed ad numbers 0-9
				self.commonGerWords.append(word)  # add lemmatized string
				word2 = re.sub('[^A-Za-züäößÄÖÜ]+', '', row[1]).lower()
				if word != word2:
					self.commonGerWords.append(word2)  # Add unformated string if not identical
		for word in other_stopwords:
			if word not in self.commonGerWords:
				self.commonGerWords.append(word)  # add additional stopwords from lib
		self.commonGerWords = set(self.commonGerWords)

	def get_word_frequency(self, article: str, just_nouns: bool = True, use_flair: bool = False) -> dict:
		"""
		Extract the most frequent words from an article body.

		:param str article: The article body
		:param bool just_nouns: focus on nouns and named entities
		:return: Topics determined from the article body.
		:rtype: dict[str: int]
		"""
		word_freq = {}
		sentence_list = nltk.sent_tokenize(article, language='german')
		for sentence in sentence_list:
			tokenized_sent = nltk.tokenize.word_tokenize(sentence, language='german')
			tokens = self.tagger.tag_sent(tokenized_sent)
			for token in tokens:
				if just_nouns and token[2] not in {'NN'}:
					continue
				if token[2] == 'NE':
					continue
				word = re.sub('[^A-Za-z0-9üäößÄÖÜ]+', '', token[1]).lower()
				if word in word_freq.keys():
					word_freq[word] = word_freq[word] + 1
				else:
					word_freq[word] = 1
			if self.use_flair and use_flair:
				flair_sentence = Sentence(sentence)
				self.flair_tagger.predict(flair_sentence)
				for named_entity in flair_sentence.get_spans('ner', .95):
					word = named_entity.text
					if word in word_freq.keys():
						word_freq[word] = word_freq[word] + 1
					else:
						word_freq[word] = 1
		return word_freq
		
	def get_topics(self, article: str) -> list:
		"""
		Extract topics from an article body.
		Hint: It is recommended to attach the headline to the body.

		:param str article: The article body
		:return: Topics determined from the article body.
		:rtype: list[str]
		"""

		word_freq = self.get_word_frequency(article)

		# remove common German words
		for commonWord in (set(word_freq.keys()) & self.commonGerWords):
			del word_freq[commonWord]

		#sort and return
		#print(sorted(word_freq.items(), key=lambda item: item[1]))	# uncomment for debugging
		result = []
		while len(result) < 5 and len(word_freq) > 0:
			topic = max(word_freq.items(), key=lambda item: item[1])
			if topic[1] <= 2:
				break
			result.append(topic[0])
			del word_freq[topic[0]]

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
	bltd = BaselineTopicDetection()
	results = bltd.get_topics(testArticle["text"])
	print(results)
	print("Test ran successfully.")