"""loads reqired NLP models fore them to be cached and not reloaded on each reboot"""
import nltk
_ = nltk.download("stopwords")
_ = nltk.download("punkt")