"""loads reqired NLP models fore them to be cached and not reloaded on each reboot"""
import nltk
from flair.models import SequenceTagger
_ = nltk.download("stopwords")
_ = nltk.download("punkt")
_ = SequenceTagger.load('de-ner')