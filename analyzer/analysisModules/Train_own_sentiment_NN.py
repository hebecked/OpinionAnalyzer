import json

# import tensorflow as tf
import numpy as np
from scipy.special import softmax
from scipy import spatial 
from textblob_de import TextBlobDE as TextBlob
import re
# from flair.models import TextClassifier
# from flair.data import Sentence
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TFBertForSequenceClassification, BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import fasttext
import fasttext.util
import nltk
import tensorflow as tf
import pandas as pd


model = BertForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")#Alternative: "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

#model.summary()
model.train()

#implement dynamic download!!!
dataset = tf.data.experimental.SqlDataset(
										driver_name = "sqlite", 
										data_source_name = "../Testdata/million-post-corpus/experiments/data/million_post_corpus/corpus.sqlite3", 
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

dataset_=[]
for data in dataset:
    if data[3].numpy() == -1:
        sentiment = [1,0,0]
    elif data[3].numpy() == 0:
        sentiment = [0,1,0]
    elif data[3].numpy() == 1:
        sentiment = [0,0,1]
    else:
        print("Error!")
    dataset_.append([data[0].numpy(), str(data[1].numpy()+data[2].numpy(), encoding="UTF-8"), sentiment])

#split in train val and test (80,10,10)
#get tokens
#Dataset class


train_dataset=dataset
val_dataset=dataset


training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size per device during training
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
)

trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset             # evaluation dataset
)

trainer.train()


#from sklearn.model_selection import train_test_split
#train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)






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