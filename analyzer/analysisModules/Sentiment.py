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
from scipy import spatial 
from textblob_de import TextBlobDE as TextBlob
import re
# from flair.models import TextClassifier
# from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import fasttext
import fasttext.util
import nltk


# from IPython import embed; embed()
class baselineSentiment:
    """
    Sentiment analyzer module based on a simple word - sentiment list.
    The average and the std of all words in a text that can be matched to a word in the list is calculated.
    """

    def __init__(self):
        #Line format: "word|POS \t sentiment \t word,word... \n"
        with open('../Testdata/SentiWS_v1.8c_Negative.txt', 'r', encoding='utf-8') as file1: 
            Lines = file1.readlines() 
        with open('../Testdata/SentiWS_v1.8c_Positive.txt', 'r', encoding='utf-8') as file2:
            Lines.extend(file2.readlines()) 
        sentiments = dict()
        for line in Lines:
            splits1 = line.split("|")
            splits2 = splits1[1].split("\t")
            word = re.sub('[^A-Za-züäößÄÖÜ]+', '', splits1[0]).lower()
            sentiment = float(splits2[1])
            sentiments[word] = sentiment
            if len(splits2)>2:
                related_words = splits2[2].split(",")
                for related_word in related_words:
                    word = re.sub('[^A-Za-züäößÄÖÜ]+', '', related_word).lower()
                    sentiments[word] = sentiment
        self.sentiments = sentiments


    def print_sentiments(self):
        """Prints all the read-in sentiments"""
        print(self.sentiments)

    def analyze(self, text):
        values=[]
        text_words = re.split('\s+', text)
        nwords=0
        for word in text_words:
            clean_word = re.sub('[^A-Za-züäößÄÖÜ]+', '', word).lower()
            if clean_word in self.sentiments.keys():
                values.append(self.sentiments[clean_word])
                nwords+=1
        if len(values) == 0:
            result = 0
            error = 1
        else:
            result = np.mean(values)
            error = np.std(values)
        self.lastbase = [nwords, len(text_words)] #allows to evaluate certainty of a result
        return [result, error] 


class baselineFastTextSentiment(baselineSentiment):
    """
    Sentiment analyzer module based on a word - sentiment list supported by fasttext-vectors.
    The average and the std of all words in a text that can be matched to a word in the list is calculated.
    To match the words the cosine distance of festtext-vectors are used.
    """

    def __init__(self):
        super().__init__() #call without lower case?
        self.ft = fasttext.load_model('../Testdata/cc.de.50.bin')
        #fasttext.util.reduce_model(self.ft, 50) #change size
        #self.ft.save_model('../Testdata/cc.de.50.bin') #and store
        ft_sentiment = []
        for word in self.sentiments:
            word_vector = self.ft.get_word_vector(word)
            ft_sentiment.append([word, word_vector, self.sentiments[word]])
        self.ft_sentiment = ft_sentiment
        self.stopwords = set(nltk.corpus.stopwords.words("german"))

    def analyze(self, text):
        values = []
        text_words = re.split('\s+', text)
        nwords = 0
        for word in text_words:
            clean_word = re.sub('[^A-Za-züäößÄÖÜ]+', '', word).lower()
            #remove stop words
            if clean_word in self.stopwords:
                continue
            nwords += 1
            #generate word vectors
            ft_word = self.ft.get_word_vector(clean_word)
            closest_distance = spatial.distance.cosine(ft_word, self.ft_sentiment[0][1])
            closest_index = 0
            #compare to all sentiment word vectors and get minimum cosine distance
            for i, reference in enumerate(self.ft_sentiment):
                distance = spatial.distance.cosine(ft_word,reference[1])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = i
            if closest_distance > 0.25:
                continue
            #print(closest_distance, clean_word, self.ft_sentiment[closest_index][0])
            values.append(self.ft_sentiment[closest_index][2])
        if len(values) == 0:
            result = 0
            error = 1
        else:
            result = np.mean(values)
            error = np.std(values)
        self.lastbase = [nwords, len(text_words)] #allows to evaluate certainty of a result
        return [result, error] 


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
        inputs = self.tokenizer(text, return_tensors="pt")  # , max_length=512, stride=0, return_overflowing_tokens=True, truncation=True, padding=True)
        length = len(inputs['input_ids'][0])
        while length > 0:
            if length > self.max_length:
                next_inputs = {k: (i[0][self.max_length:]).reshape(1, len(i[0][self.max_length:])) for k, i in inputs.items()}  
                inputs = {k: (i[0][:self.max_length]).reshape(1, len(i[0][:self.max_length])) for k, i in inputs.items()}
            else:
                next_inputs = False
            proOrCon = self.model(**inputs)
            weights = proOrCon[0].detach().numpy()[0]
            weights = softmax(weights)
            average = np.average(np.linspace(1, 5, 5), weights=weights)
            average_scaled = (average -1) * 2. / 4. - 1
            averages.append(average_scaled)
            errors.append(
                np.sqrt(np.average((np.linspace(-1, 1, 5) - average_scaled) ** 2, weights=weights))
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
    https://github.com/oliverguhr/german-sentiment
    """

    def __init__(self, truncate=False):
        self.tokenizer = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")
        self.model = AutoModelForSequenceClassification.from_pretrained("oliverguhr/german-sentiment-bert")
        self.truncate = truncate
        self.max_length = 512

    def analyze(self, text):
        averages = []
        errors = []
        inputs = self.tokenizer(text, return_tensors="pt")  # , max_length=512, stride=0, return_overflowing_tokens=True, truncation=True, padding=True)
        length = len(inputs['input_ids'][0])
        while length > 0:
            if length > self.max_length:
                next_inputs = {k: (i[0][self.max_length:]).reshape(1, len(i[0][self.max_length:])) for k, i in inputs.items()}
                inputs = {k: (i[0][:self.max_length]).reshape(1, len(i[0][:self.max_length])) for k, i in inputs.items()}
            else:
                next_inputs = False
            proOrCon = self.model(**inputs)
            weights = proOrCon[0].detach().numpy()[0]
            weights[2], weights[1] = weights[1], weights[2] # reorder for linear scaling according to model output
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
        error = np.sqrt(1. / np.sum(1. / np.array(errors) ** 2)) #*5./3.
        return [average, error]


class custom_model_sentiment:
    """
    Sentiment analyzer module based on custom trained NN-models
    """

    def __init__(self, model_path, tokenizer_path, truncate=False):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path) #3 Classes in the following order: Negative, Neutral, Positive,
        self.truncate = truncate
        self.max_length = 512

    def analyze(self, text):
        averages = []
        errors = []
        inputs = self.tokenizer(text, return_tensors="pt")  # , max_length=512, stride=0, return_overflowing_tokens=True, truncation=True, padding=True)
        length = len(inputs['input_ids'][0])
        while length > 0:
            if length > self.max_length:
                next_inputs = {k: (i[0][self.max_length:]).reshape(1, len(i[0][self.max_length:])) for k, i in inputs.items()}
                inputs = {k: (i[0][:self.max_length]).reshape(1, len(i[0][:self.max_length])) for k, i in inputs.items()}
            else:
                next_inputs = False
            proOrCon = self.model(**inputs)
            weights = proOrCon[0].detach().numpy()[0]
            weights = softmax(weights)
            average = np.average(np.linspace(-1, 1, 3), weights=weights)
            averages.append(average)
            errors.append(
                np.sqrt(np.average(np.array(np.linspace(-1, 1, 3) - average) ** 2, weights=weights))
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
        error = np.sqrt(1. / np.sum(1. / np.array(errors) ** 2)) #*5./3.
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
        #sqrt__weighted_variance = np.sqrt(np.average((results.T[0] - result) ** 2, weights=1. / results.T[1] ** 2)) # Error determination including discrepancy between outputs 
        error = np.sqrt(1. / np.sum(1. / results.T[1] ** 2)) # physically correct error determination
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

    models = {"multilang_bert_sentiment":"", "german_bert_sentiment":"", "EnsembleSentiment":"", "baselineSentiment":"", "baselineFastTextSentiment":"", "TextblobSentiment":""}#, "custom_model_sentiment":""}
    print("Loading NLP models.")
    model_objects=dict()
    for model in models.keys():
        parameter = models[model]
        exec("model_objects[model] = %s(\"%s\")" % (model, parameter))

    print("Running ", Test_cases, " tests + one overlength sample.")
    accu = []
    for i, comment in enumerate(testComments):
        if comment["user"] is not None and comment["body"] is not None:
            # sentence = Sentence(comment["body"])
            # Tourette = classifier.predict(sentence)
            results = dict()
            for model in model_objects.keys():
                results[model] =  model_objects[model].analyze(comment["body"])
            result_string = str().join([model + ": " + str(results[model]) + "\n"  for model in results.keys()])
            print("Comment " + str(i) + ":\n", comment["body"], "\n\n" + result_string)
            accu.extend(comment["body"])

            
        if i >= Test_cases:
            break
    accu = str().join(accu)
    results = dict()
    for model in model_objects.keys():
        results[model] =  model_objects[model].analyze(accu)
    result_string = str().join([model + ": " + str(results[model]) + "\n"  for model in results.keys()])
    print("Large comment: \n", "---Long text omitted---", "\n", result_string)
    print("Tests completed successfully.")


