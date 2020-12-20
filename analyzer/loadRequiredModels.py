#loads reqired NLP models fore them to be cached and not reloaded on each reboot
from transformers import AutoTokenizer, AutoModelForSequenceClassification

_ = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
_ = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
_ = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")
_ = AutoModelForSequenceClassification.from_pretrained("oliverguhr/german-sentiment-bert")