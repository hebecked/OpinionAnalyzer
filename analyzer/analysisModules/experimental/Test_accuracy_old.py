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
#from Sentiment import custom_model_sentiment

class DatasetCorpus(torch.utils.data.Dataset):
    """Container class to supply dataset content to the training algorithm."""

    def __init__(self, dataset):
        encodings = dict()
        encodings["input_ids"] = dataset["input_ids"]
        encodings["attention_mask"] = dataset["attention_mask"]
        self.encodings = encodings
        self.labels = [torch.tensor(i) for i in dataset["labels"]]
        self.data = dataset

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx]).clone().detach()
        return item

    def __len__(self):
        return len(self.labels)



print("Loading pretrained model.")
model = AutoModelForSequenceClassification.from_pretrained("../models/new_balanced_model")
tokenizer = BertTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")


print("Read datasets from file.")
with open( '../Testdata/test_dataset.json', 'r') as fp:
    test_dataset = json.load(fp)

print("Test dataset size:", len(test_dataset["text_input"]))

#convert numpy label arrays to pytorch tensors
print("Creating tokens...")# tokens
test_tokens = tokenizer(test_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
test_dataset.update(test_tokens)
print("Done.")


test_dataset=DatasetCorpus(test_dataset)

print("Testing:")
device = torch.device("cpu")
model.to(device)
model.eval()
for i, test_data in enumerate(test_dataset):
    test_data["input_ids"] = test_data["input_ids"].reshape([1,-1])
    test_data['attention_mask'] = test_data['attention_mask'].reshape([1,-1])
    label=test_data.pop("labels").reshape([1,-1])
    result = model(**test_data)
    print(test_dataset.data["text_input"][i])
    print(label, softmax(result.logits.detach().numpy()), i, "\n")
    #print(result)
    if i > 10:
        break

print("Calculating accuracy.\nThis may take a while...")
match = 0
#set a limit to speed-up the evaluation and reduce the sample size used 
limit = None
for i, test_data in enumerate(test_dataset):
    test_data["input_ids"]= test_data["input_ids"].reshape([1,-1])
    test_data['attention_mask']= test_data['attention_mask'].reshape([1,-1])
    label=test_data.pop("labels").reshape([1,-1])
    result = model(**test_data) 
    sentiment = np.argmax(softmax(result.logits.detach().numpy()))
    match += label.numpy()[0][sentiment]
    if limit is not None and i >= limit:
        break 
if limit is not None:
    sample_size = float(limit)
else:
    sample_size = float(len(test_dataset))
accuracy = float(match) / sample_size
print("Done\nThe model has an accuracy of", accuracy, "\nThis is based on a sample size of", sample_size)
