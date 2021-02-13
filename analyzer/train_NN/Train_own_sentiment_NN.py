import json
import torch
import os
import numpy as np
import pandas as pd
from scipy.special import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TFBertForSequenceClassification, BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments, AdamW, PretrainedConfig
from torch.nn import BCEWithLogitsLoss, BCELoss
from torch import nn
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler


print("Read datasets from file.")
datasets = {"train_dataset": None, "val_dataset": None, "test_dataset": None}
for dataset in datasets.keys():
    with open( "../Testdata/" + dataset + '_dataset.json', 'r') as fp:
        datasets[dataset] = json.load(fp)


#convert numpy label arrays to pytorch tensors
print("Creating tokens...")# tokens
train_tokens = tokenizer(train_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
train_dataset.update(train_tokens)
val_tokens = tokenizer(val_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
val_dataset.update(val_tokens)
test_tokens = tokenizer(test_dataset["text_input"], truncation=True, padding=True, return_tensors="pt")
test_dataset.update(test_tokens)
print("Done.")

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
config["model_type"]= "bert"
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
