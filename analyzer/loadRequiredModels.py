"""loads reqired NLP models fore them to be cached and not reloaded on each reboot"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import nltk
import fasttext.util
import OS

_ = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
_ = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
_ = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")
_ = AutoModelForSequenceClassification.from_pretrained("oliverguhr/german-sentiment-bert")
_ = nltk.download("stopwords")
fasttext.util.download_model('de', if_exists='ignore')
ft = fasttext.load_model('cc.de.300.bin')
fasttext.util.reduce_model(ft, 50)
ft.save_model('./Testdata/cc.de.50.bin')
os.remove('cc.de.300.bin')
os.remove('cc.de.300.bin.gz')