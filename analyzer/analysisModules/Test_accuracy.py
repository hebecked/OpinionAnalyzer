import json
import torch
import os
import numpy as np
import pandas as pd
from scipy.special import softmax
#from transformers import AutoTokenizer, AutoModelForSequenceClassification, TFBertForSequenceClassification, BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments, AdamW, PretrainedConfig
from torch.nn import BCEWithLogitsLoss, BCELoss
from torch import nn
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import *
from transformers.modeling_outputs import SequenceClassifierOutput
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from Sentiment import *
import time



models = {  "multilang_bert_sentiment":"", 
            "german_bert_sentiment":"", 
            "EnsembleSentiment":"output_all_results = False", 
            "baselineSentiment":"", 
            "baselineFastTextSentiment":"", 
            "TextblobSentiment":"", 
            "custom_model_sentiment":"model_path='../models/new_balanced_model', tokenizer_path='nlptown/bert-base-multilingual-uncased-sentiment'"
            }
print("Loading NLP models.")
model_objects=dict()
for model in models.keys():
    parameter = models[model]
    print("Loading: " + model + " " + parameter)
    exec("model_objects[model] = %s(%s) " % (model, parameter))



print("Read datasets from file.")
datasets = ["accuracy_dataset.json", "test_dataset.json"]
with open( '../Testdata/' + datasets[1], 'r') as fp:
    test_dataset = json.load(fp)

print("Test dataset size:", len(test_dataset["text_input"]))



print("Calculating accuracy.\nThis may take a while...")
match = dict()
for model in model_objects.keys():
    match[model] = np.array([0,0,0])
#set a limit to speed-up the evaluation and reduce the sample size used 
limit = 100 #None
for i, test_data in enumerate(test_dataset["text_input"]):
    truth = test_dataset["labels"][i]
    for model in model_objects.keys():
        result =  model_objects[model].analyze(test_data)
        if result[0] < -0.33:
            sentiment = -1
        elif result[0] < 0.33:
            sentiment = 0
        else:
            sentiment = 1
        match[model][sentiment+1] += truth[sentiment+1]
    if limit is not None and i >= limit:
        break 
if limit is not None and limit < float(len(test_dataset["text_input"])):
    sample_size = float(limit)
else:
    sample_size = float(len(test_dataset["text_input"]))
for model in model_objects.keys():
    accuracy = float(np.sum(match[model])) / sample_size
    class_sample_size = np.sum(test_dataset["labels"][0:limit],0)
    print("Done\nThe model " + model + " has an accuracy of", accuracy)
    print("Done\nThe model " + model + " has an individual class accuracy of", match[model]/class_sample_size)
print("This is based on a sample size of", sample_size, "Split according to:", class_sample_size)


print("\nWaiting 20 seconds to continue individual tests.")
time.sleep(20)

print("Testing:")
for i, test_data in enumerate(test_dataset["text_input"]):
    print(test_data, "\nTruth " + str(i)+ ":", test_dataset["labels"][i])
    for model in model_objects.keys():
        result =  model_objects[model].analyze(test_data)
        print(model + ":", result)
    print("\n")
    #print(result)
    if i > 10:
        break
