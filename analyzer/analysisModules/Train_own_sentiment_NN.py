import json

# import tensorflow as tf
import numpy as np
from scipy.special import softmax
#from scipy import spatial 
#from textblob_de import TextBlobDE as TextBlob
#import re
# from flair.models import TextClassifier
# from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TFBertForSequenceClassification, BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments, AdamW, PretrainedConfig
#import fasttext
#import fasttext.util
#import nltk
import tensorflow as tf
import pandas as pd
import torch
import wget
import tarfile
import os
from torch.nn import BCEWithLogitsLoss, BCELoss
from torch import nn
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler

if not os.path.isfile("million_post_corpus.tar.bz2") and not os.path.isfile("million_post_corpus/corpus.sqlite3"):
    dataset_URL = "https://github.com/OFAI/million-post-corpus/releases/download/v1.0.0/million_post_corpus.tar.bz2"
    wget.download(dataset_URL)

if not os.path.isfile("million_post_corpus/corpus.sqlite3"):
    tar = tarfile.open("million_post_corpus.tar.bz2", "r:bz2")  
    tar.extract("million_post_corpus/corpus.sqlite3") #corpus.sqlite3
    tar.close()

if os.path.isfile("million_post_corpus.tar.bz2"):  
    os.remove("million_post_corpus.tar.bz2") 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_gpu = torch.cuda.device_count()
#torch.cuda.get_device_name(0)

model = BertForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")#, num_labels=6)#Alternative: "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

#model.summary()
#model.cuda()

#Send DB output to Akbik
# use and modify https://huggingface.co/transformers/_modules/transformers/models/bert/modeling_bert.html#BertForSequenceClassification
dataset = tf.data.experimental.SqlDataset(
										driver_name = "sqlite", 
										data_source_name = "./million_post_corpus/corpus.sqlite3", 
										query = '''
                                            SELECT
                                                p.ID_Post,
                                                p.Headline,
                                                p.Body,
                                                CASE 
                                                    WHEN ac.Category = 'SentimentNegative' THEN -1
                                                    WHEN ac.Category = 'SentimentNeutral' THEN 0
                                                    WHEN ac.Category = 'SentimentPositive' THEN 1
                                                    ELSE NULL
                                                END
                                            FROM
                                                Posts p
                                                INNER JOIN Annotations_consolidated ac ON p.ID_Post = ac.ID_Post
                                            WHERE
                                                ac.Category IN ('SentimentNegative', 'SentimentNeutral', 'SentimentPositive')
                                                AND ac.Value = 1
										        ;
										    ''', 
										output_types = (tf.int32, tf.string, tf.string, tf.int32)
										)


import csv
with open('../Testdata/dataset.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i, data in enumerate(dataset):
        spamwriter.writerow([data[0].numpy(), str(data[1].numpy(), encoding="UTF-8"), str(data[2].numpy(), encoding="UTF-8"), data[3].numpy()])

#split in train val and test (80,10,10)

combined_dataset = []
for data in dataset:
    combined_dataset.append([str(data[1].numpy(), encoding="UTF-8") + "\n" + str(data[2].numpy(), encoding="UTF-8"), data[3].numpy()])
    if data[1].numpy() is not "":
        combined_dataset.append([str(data[2].numpy(), encoding="UTF-8"), data[3].numpy()])

original_length=len(combined_dataset)
for i, data in enumerate(combined_dataset):
    for j in range(original_length-i-1):
        if data[1] == combined_dataset[j+1][1]:
            combined_dataset.append([data[0] + " " + combined_dataset[j+1][0], data[1]])


train_dataset = {"labels": [], 'text_input': []}
val_dataset = {"labels": [], 'text_input': []}
test_dataset = {"labels": [], 'text_input': []}
for i, data in enumerate(combined_dataset):
    if  data[1] == -1:
        sentiment = [1., 0., 0.]
    elif data[1] == 0:
        sentiment = [0., 1., 0.]
    elif data[1] == 1:
        sentiment = [0., 0., 1.]
    else:
        print("Error!")
    if i % 10 == 0:
        test_dataset["labels"].append(sentiment)
        test_dataset["text_input"].append( data[0] )
    elif i % 10 -1 == 0:
        val_dataset["labels"].append(sentiment)
        val_dataset["text_input"].append( data[0] )
    else:
        train_dataset["labels"].append(sentiment)
        train_dataset["text_input"].append( data[0] )

#convert numpy label arrays to pytorch tensors

#get tokens
train_tokens = tokenizer(train_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
train_dataset.update(train_tokens)
val_tokens = tokenizer(val_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
val_dataset.update(val_tokens)
test_tokens = tokenizer(test_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
test_dataset.update(test_tokens)


#Dataset class
class DatasetCorpus(torch.utils.data.Dataset):
    def __init__(self, dataset):
        encodings = dict()
        encodings["input_ids"] = dataset["input_ids"]
        encodings["attention_mask"] = dataset["attention_mask"]
        self.encodings = encodings
        self.labels = [torch.tensor(i) for i in dataset["labels"]]
        self.data = dataset

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)



train_dataset=DatasetCorpus(train_dataset)
val_dataset=DatasetCorpus(val_dataset)
test_dataset=DatasetCorpus(test_dataset)
#

#Instructions for manual training: https://towardsdatascience.com/transformers-for-multilabel-classification-71a1a0daf5e1
#optimizer = AdamW(model.parameters(),lr=2e-5) # pytorch ! #learning_rate=3e-5 ?
loss = BCEWithLogitsLoss()
model.classifier = nn.Linear(768,3)
model.num_labels = 3
model.train()

#model.compile(optimizer=optimizer, loss=loss)

training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size per device during training (16)?
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
)

class MyTrainer(Trainer):
    def compute_loss(self, model, inputs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs[0]
        return loss(logits, labels)

trainer = MyTrainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset             # evaluation dataset
)

print("Starting training")
#exit()
trainer.train()



#torch.save(model.state_dict(), 'results/bert_self_trained_model') 
config = model.config
config = config.to_dict()
config["_num_labels"] = 3
config['id2label'] = {'0': 'NEGATIVE',
   '1': 'NEUTRAL',
   '2': 'POSITIVE'}
config['label2id'] = {'NEGATIVE': 0,
   'NEUTRAL': 1,
   'POSITIVE': 2}
model.config = PretrainedConfig.from_dict(config)
model.save_pretrained("./results/bert_self_trained_model")
tokenizer
#os.remove("./results/bert_self_trained_model/config.json") 
#PretrainedConfig.get_config_dict("nlptown/bert-base-multilingual-uncased-sentiment")
#new_config = PretrainedConfig.from_dict(new_config_dic)
#new_config.save_pretrained("./results/bert_self_trained_model")
os.remove("million_post_corpus/corpus.sqlite3") 
os.removedirs("million_post_corpus") 

print("Testing:")
device = torch.device("cpu")
model.to(device)
model.eval()
for i, test_data in enumerate(test_dataset):
    test_data["input_ids"]= test_data["input_ids"].reshape([1,-1])
    test_data['attention_mask']= test_data['attention_mask'].reshape([1,-1])
    label=test_data.pop("labels").reshape([1,-1])
    result = model(**test_data) 
    print(test_dataset.data["text_input"][i])
    print(label, softmax(result.logits.detach().numpy()))
    print(result)

#The following contains different versions of the SQL Query
'''
    SELECT Posts.ID_Post, Headline, Body, Value
    FROM Posts INNER JOIN Annotations_consolidated
    ON Posts.ID_Post = Annotations_consolidated.ID_Post
    WHERE Category = "SentimentNegative" or Category = "SentimentNeutral" or Category = "SentimentPositive"
    ;
'''


"""
WITH proof AS (
SELECT
    p.ID_Post,
    p.Headline,
    p.Body,
    CASE 
        WHEN ac.Category = 'SentimentNegative' THEN -1
        WHEN ac.Category = 'SentimentNeutral' THEN 0
        WHEN ac.Category = 'SentimentPositive' THEN 1
        ELSE NULL
    END
FROM
    Posts p
    INNER JOIN Annotations_consolidated ac ON p.ID_Post = ac.ID_Post
WHERE
    ac.Category IN ('SentimentNegative', 'SentimentNeutral', 'SentimentPositive')
    AND ac.Value = 1)
SELECT
  COUNT(ID_Post) AS count,
  COUNT(DISTINCT ID_Post) AS distinct_count
FROM
  proof
"""
