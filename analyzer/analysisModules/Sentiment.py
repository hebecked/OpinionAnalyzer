"""
TODO:

Libs to add: Topic detection, big 5 personality traits, IQ/Education, origin, wordcount, spelling, offensiveLanguage detection, mood
Sources:
Prep text (bag of words): 	https://monkeylearn.com/topic-analysis/
							https://towardsdatascience.com/nlp-extracting-the-main-topics-from-your-dataset-using-lda-in-minutes-21486f5aa925
Get text topic:	https://spacy.io/models/de
				Reduce article(s) to a few representative words (Top N = 8(?) words in (maximum word frequency - common words)) 
				(ML-NLP approaches, gpt summary?)
Get Personalities: 	https://github.com/jkwieser/personality-detection-text
					https://github.com/SenticNet/personality-detection
"""

import json

# import tensorflow as tf
import numpy as np
from scipy.special import softmax
from textblob_de import TextBlobDE as TextBlob
# from flair.models import TextClassifier
# from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# from IPython import embed; embed()


class multilang_bert_sentiment:
    """
    Sentiment analyzer module based on Amazonreview (1-5 stars)
    #https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment?text = Nicht+kaufen
    """

    def __init__(self, truncate=False):
        self.tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "nlptown/bert-base-multilingual-uncased-sentiment")
        self.truncate = truncate
        self.max_length = 512

    def analyze(self, text):
        averages = []
        errors = []
        inputs = self.tokenizer(text,
                                return_tensors="pt")  # , max_length=512, stride=0, return_overflowing_tokens=True, truncation=True, padding=True)
        length = len(inputs['input_ids'][0])
        while length > 0:
            if length > self.max_length:
                next_inputs = {k: (i[0][self.max_length:]).reshape(1, len(i[0][self.max_length:])) for k, i in
                               inputs.items()}
                inputs = {k: (i[0][:self.max_length]).reshape(1, len(i[0][:self.max_length])) for k, i in
                          inputs.items()}
            else:
                next_inputs = False
            proOrCon = self.model(**inputs)
            weights = proOrCon[0].detach().numpy()[0]
            weights = softmax(weights)
            average = np.average(np.linspace(1, 5, 5), weights=weights)
            average = average * 2. / 5. - 1
            averages.append(average)
            errors.append(
                np.sqrt(np.average((np.linspace(1, 5, 5) - average) ** 2, weights=weights)) * 2. / 5.
            )
            if self.truncate:
                break
            if next_inputs:
                inputs = next_inputs
            else:
                break
            length = len(inputs['input_ids'][0])
        average = np.average(averages, weights=1. / np.array(errors) ** 2)
        error = np.sqrt(1. / np.sum(1. / np.array(errors) ** 2))
        return [average, error]


class german_bert_sentiment:
    """
    Sentiment analyzer module based on a range of sources including twitter, facebook, product reviews
    https://huggingface.co/oliverguhr/german-sentiment-bert?text = Du+Arsch%21
    """

    def __init__(self, truncate=False):
        self.tokenizer = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")
        self.model = AutoModelForSequenceClassification.from_pretrained("oliverguhr/german-sentiment-bert")
        self.truncate = truncate
        self.max_length = 512

    def analyze(self, text):
        averages = []
        errors = []
        inputs = self.tokenizer(text,
                                return_tensors="pt")  # , max_length=512, stride=0, return_overflowing_tokens=True, truncation=True, padding=True)
        length = len(inputs['input_ids'][0])
        while length > 0:
            if length > self.max_length:
                next_inputs = {k: (i[0][self.max_length:]).reshape(1, len(i[0][self.max_length:])) for k, i in
                               inputs.items()}
                inputs = {k: (i[0][:self.max_length]).reshape(1, len(i[0][:self.max_length])) for k, i in
                          inputs.items()}
            else:
                next_inputs = False
            proOrCon = self.model(**inputs)
            weights = proOrCon[0].detach().numpy()[0]
            weights[2], weights[1] = weights[1], weights[2]
            weights = softmax(weights)
            average = np.average(np.linspace(1, -1, 3), weights=weights)
            averages.append(average)
            errors.append(
                np.sqrt(np.average(np.array(np.linspace(1, -1, 3) - average) ** 2, weights=weights))
            )
            # from IPython import embed; embed()
            if self.truncate:
                break
            if next_inputs:
                inputs = next_inputs
            else:
                break
            length = len(inputs['input_ids'][0])
        average = np.average(averages, weights=1. / np.array(errors) ** 2)
        error = np.sqrt(1. / np.sum(1. / np.array(errors) ** 2))
        return [average, error]


class TextblobSentiment:
    """
    More information at https://textblob-de.readthedocs.io/en/latest/ and https://github.com/sloria/TextBlob/
    https://machine-learning-blog.de/2019/06/03/stimmungsanalyse-sentiment-analysis-auf-deutsch-mit-python/
    """

    def __init__(self):
        pass

    def analyze(self, text):
        blob = TextBlob(text)
        mood = blob.sentiment
        return [mood.polarity, 1]  # use an error of 1 for compatibility and because results are very unreliable

    def analyzeSubjectivity(self, text):
        blob = TextBlob(text)
        mood = blob.sentiment
        return mood.subjectivity


class EnsembleSentiment():
    """Sentiment analyzer module combining the first two modules based on error weighted mean."""

    def __init__(self):
        # Based on Amazonreview (1-5 stars)
        self.sentiment_model_1 = multilang_bert_sentiment()
        # Based on a range of sources including twitter, facebook, product reviews
        self.sentiment_model_2 = german_bert_sentiment()

    def analyze(self, text):
        result1 = self.sentiment_model_1.analyze(text)
        result2 = self.sentiment_model_2.analyze(text)
        results = np.array([result1, result2])
        result = np.average(results.T[0], weights=1. / results.T[1] ** 2)
        error = np.sqrt(1. / np.sum(1. / results.T[1] ** 2))
        return [result, error]


# classifier = TextClassifier.load('de-offensive-language') # en-sentiment


if __name__ == "__main__":
    '''Run some test scenarios'''

    Test_cases = 10
    with open('../Testdata/TestArticle.json') as f:
        testArticle = json.load(f)
    # dict_keys(['url', 'id', 'channel', 'subchannel', 'headline', 'intro', 'text', 'topics', 'author', 'comments_enabled', 'date_created', 'date_modified', 'date_published', 'breadcrumbs'])

    with open('../Testdata/TestComments.json') as f:
        testComments = json.load(f)

    print("Loading NLP models.")
    SentimentModel1 = multilang_bert_sentiment()
    SentimentModel2 = german_bert_sentiment(truncate=True)
    SentimentModel3 = EnsembleSentiment()

    print("Running ", Test_cases, " tests + one overlength sample.")
    accu = []
    for i, comment in enumerate(testComments):
        if comment["user"] is not None and comment["body"] is not None:
            # sentence = Sentence(comment["body"])
            # Tourette = classifier.predict(sentence)

            result1 = SentimentModel1.analyze(comment["body"])
            result2 = SentimentModel2.analyze(comment["body"])
            result3 = SentimentModel3.analyze(comment["body"])
            result4 = TextblobSentiment().analyze(comment["body"])
            accu.extend(comment["body"])
            print("Comment: ", i, " Results 1,2,3,4: ", result1, result2, result3, result4)
        if i >= Test_cases:
            break
    accu = str().join(accu)
    result1 = SentimentModel1.analyze(accu)
    result2 = SentimentModel2.analyze(accu)
    result3 = SentimentModel3.analyze(accu)
    result4 = TextblobSentiment().analyze(accu)
    print("Large Comment Results 1,2,3,4: ", result1, result2, result3, result4)
    print("Tests completed successfully.")
