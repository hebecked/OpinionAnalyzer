import json
import numpy as np
import os
import csv
from random import shuffle

"""
This program prepares an additional test dataset from independent self labeled data. 
"""

test_dataset=[]
count = [0, 0, 0]
print("Reading sentiments that were manually annotated.")
sources = {"positive", "neutral", "negative"}
for source in sources:
    with open('../Testdata/' + source + '_labels_for_accuracy_test.csv', newline='', encoding='utf-8') as csvfile:
        readfile = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in readfile:
            if row[3] != "" and row[4] == "" and row[2] != "":
                count[int(row[3])+1]+=1
                test_dataset.append([row[2], int(row[3])])
print("Done.")
print("Data distribution [Negative, Neutral, Positive]:", count)
shuffle(test_dataset)



print("Preping Dataset.")
dataset = {"labels": [], 'text_input': []}
for i, data in enumerate(test_dataset):
    if  data[1] == -1:
        sentiment = [1., 0., 0.]
    elif data[1] == 0:
        sentiment = [0., 1., 0.]
    elif data[1] == 1:
        sentiment = [0., 0., 1.]
    else:
        print("Error!\n", data[1])
    dataset["labels"].append(sentiment)
    dataset["text_input"].append( data[0] )


print("Writing datasets to file.")
with open( '../Testdata/accuracy_dataset.json', 'w') as fp:
    json.dump(dataset, fp)
