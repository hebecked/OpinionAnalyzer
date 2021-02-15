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

class BertForMultiLabelSequenceClassification(BertForSequenceClassification): # For newer version use BertPreTrainedModel,For older versions use: PreTrainedBertModel
    """BERT model for classification.
    This module is composed of the BERT model with a linear layer on top of
    the pooled output.
    """

    def __init__(self, config):
        super(BertForMultiLabelSequenceClassification, self).__init__(config)
        self.bert = BertModel(config)

    def reconfigure(self, num_labels=3):
        self.num_labels = num_labels
        self.dropout = torch.nn.Dropout(self.config.hidden_dropout_prob)
        self.classifier = torch.nn.Linear(self.config.hidden_size, num_labels)
        self.init_weights()
        #self.apply(self.init_bert_weights)
        config = self.config.to_dict()
        config["_num_labels"] = 3
        config['id2label'] = {'0': 'NEGATIVE',
           '1': 'NEUTRAL',
           '2': 'POSITIVE'}
        config['label2id'] = {'NEGATIVE': 0,
           'NEUTRAL': 1,
           'POSITIVE': 2}
        config["model_type"]= "bert"
        self.config = PretrainedConfig.from_dict(config)
 
    def forward(self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        labels=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        loss = None
        if labels is not None:
            loss_fct = BCEWithLogitsLoss()
            loss = loss_fct(logits.view(-1), labels.view(-1)) #, self.num_labels

        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
        
    def freeze_bert_encoder(self):
        for param in self.bert.parameters():
            param.requires_grad = False
    
    def unfreeze_bert_encoder(self):
        for param in self.bert.parameters():
            param.requires_grad = True


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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_gpu = torch.cuda.device_count()
#torch.cuda.get_device_name(0)

print("Loading pretrained model.")
pretrained_source = "nlptown/bert-base-multilingual-uncased-sentiment"
#pretrained_source = "oliverguhr/german-sentiment-bert"
#pretrained_source = "bert-base-uncased"
model = BertForMultiLabelSequenceClassification.from_pretrained(pretrained_source) #Alternative: "bert-base-uncased"
model.reconfigure(num_labels=3) # replace this even for matching models !
tokenizer = BertTokenizer.from_pretrained(pretrained_source)


print("Read datasets from file.")
datasets = {"train_dataset": None, "val_dataset": None, "test_dataset": None}
for dataset in datasets.keys():
    with open( "../Testdata/" + dataset + '.json', 'r') as fp:
        datasets[dataset] = json.load(fp)

#print("Traindataset size:", len(datasets["train_dataset"]["text_input"]))

#convert numpy label arrays to pytorch tensors
print("Creating tokens...")# tokens
train_tokens = tokenizer(datasets["train_dataset"]["text_input"], truncation=True, padding=True, return_tensors="pt")
datasets["train_dataset"].update(train_tokens)
val_tokens = tokenizer(datasets["val_dataset"]["text_input"], truncation=True, padding=True, return_tensors="pt")
datasets["val_dataset"].update(val_tokens)
test_tokens = tokenizer(datasets["test_dataset"]["text_input"], truncation=True, padding=True, return_tensors="pt")
datasets["test_dataset"].update(test_tokens)
print("Done.")


train_dataset=DatasetCorpus(datasets["train_dataset"])
val_dataset=DatasetCorpus(datasets["val_dataset"])
test_dataset=DatasetCorpus(datasets["test_dataset"])
#

#Instructions for manual training: https://towardsdatascience.com/transformers-for-multilabel-classification-71a1a0daf5e1
#optimizer = AdamW(model.parameters(),lr=2e-5) # pytorch ! #learning_rate=3e-5 ?

#model.to(device)
model.train()

#model.compile(optimizer=optimizer, loss=loss)

training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size per device during training (16)?
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./results/logs',    # directory for storing logs
    logging_steps=10,
)

loss = BCEWithLogitsLoss()
class MyTrainer(Trainer):
    def compute_loss(self, model, inputs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs[0]
        return loss(logits, labels)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

trainer = MyTrainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset,            # evaluation dataset
    compute_metrics=compute_metrics
)

print("Starting training")
#exit()
trainer.train()



model.save_pretrained("../models/bert_self_trained_model")


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
    if i > 10:
        break

print("The accuracy will be determined now. (The program may be canceled at this point.)")
match = 0
for i, test_data in enumerate(test_dataset):
    test_data["input_ids"]= test_data["input_ids"].reshape([1,-1])
    test_data['attention_mask']= test_data['attention_mask'].reshape([1,-1])
    label=test_data.pop("labels").reshape([1,-1])
    result = model(**test_data) 
    sentiment = np.argmax(softmax(result.logits.detach().numpy()))
    match += label[0][sentiment]
accuracy = float(match) / float(len(test_dataset)) 
print("The model has an accuracy of", accuracy)