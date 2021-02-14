import json
import numpy as np
import tensorflow as tf
import pandas as pd
import torch
import wget
import tarfile
import os
import csv
from random import shuffle
from torch.nn import BCEWithLogitsLoss, BCELoss
from torch import nn
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler

print("Checking if DB is available otherwise it will be downlaoded.")
if not os.path.isfile("million_post_corpus.tar.bz2") and not os.path.isfile("million_post_corpus/corpus.sqlite3"):
    print("Downloading ...")
    dataset_URL = "https://github.com/OFAI/million-post-corpus/releases/download/v1.0.0/million_post_corpus.tar.bz2"
    wget.download(dataset_URL)

if not os.path.isfile("million_post_corpus/corpus.sqlite3"):
    print("\nExtracting ...")
    tar = tarfile.open("million_post_corpus.tar.bz2", "r:bz2")  
    tar.extract("million_post_corpus/corpus.sqlite3") #corpus.sqlite3
    tar.close()

if os.path.isfile("million_post_corpus.tar.bz2"):  
    os.remove("million_post_corpus.tar.bz2") 
print("Done.")

print("Reading from DB.")
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



count = [0,0,0]
original_dataset = []
for data in dataset:
    count[data[3].numpy()+1]+=1
    if data[1].numpy() != "" or data[2].numpy() != "":
        if data[1].numpy() != "":
            original_dataset.append([str(data[1].numpy(), encoding="UTF-8") + "\n" + str(data[2].numpy(), encoding="UTF-8"), data[3].numpy()])
        original_dataset.append([str(data[2].numpy(), encoding="UTF-8"), data[3].numpy()])


with open('../Testdata/positive_labeled_comments.csv', newline='') as csvfile:
    readfile = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in readfile:
        if row[3] == "1" and row[4] == "" and row[2] != "":
            count[2]+=1
            original_dataset.append([row[2], 1])
print("Done.")
print("Original data distribution [Negative, Neutral, Positive]:", count)
shuffle(original_dataset)


print("Creating additional training data...")
original_length = len(original_dataset)
extended_dataset = []
count2 = [0,0,0]
for i, data in enumerate(original_dataset):
    for j in range(original_length-i-1):
        if data[1] == original_dataset[i+j+1][1] and (len(data[0]) + len(original_dataset[i+j+1][0])) < 512:
            count2[data[1]+1]+=1
            extended_dataset.append([data[0] + " " + original_dataset[i+j+1][0], data[1]])
shuffle(extended_dataset)
print("Done.")
print("Generated data distribution [Negative, Neutral, Positive]:", count2)

count3 = count.copy()
for i, num in enumerate(count2):
    count3[i] += num
label_set_size = min(count3)
print("Merging original and generated data with", label_set_size, "elements for each sentiment.")
for sentiment in [-1,0,1]:
    j = 0
    for i in range(label_set_size-count[sentiment+1]):
        while extended_dataset[j][1] != sentiment and j < len(extended_dataset):
            j += 1
        if j >= len(extended_dataset):
            print("Error!!!")
            break
        original_dataset.append(extended_dataset[j])

shuffle(original_dataset)
print("Done.")

print("Splitting in train, val and test dataset with a ratio (80,10,10)")
train_dataset = {"labels": [], 'text_input': []}
val_dataset = {"labels": [], 'text_input': []}
test_dataset = {"labels": [], 'text_input': []}
for i, data in enumerate(original_dataset):
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


print("Writing datasets to file.")
datasets = {"train_dataset": train_dataset, "val_dataset": val_dataset, "test_dataset": test_dataset}
for dataset in datasets.keys():
    with open( "../Testdata/" + dataset + '_dataset.json', 'w') as fp:
        json.dump(datasets[dataset], fp)

print("Cleaning up.")
os.remove("million_post_corpus/corpus.sqlite3") 
os.removedirs("million_post_corpus") 