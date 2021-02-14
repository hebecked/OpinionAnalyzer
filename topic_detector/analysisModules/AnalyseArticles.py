from utils.connectDb import Database
from utils.databaseExchange import DatabaseExchange
from TopicDetection import BaselineTopicDetection
import json
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()


#init DB exchange module
db = DatabaseExchange()

#init baseline topic detection for analysis
bltd = BaselineTopicDetection(False)

#add a loop here
articles = db.fetch_topicizer_data()  # list of {article_body_id : dict {body: , headline: ,topics: } }
result_list = []
for article_body_id, article in articles.items():
	analyze = article["headline"] + " " + article["body"]
	
	#determine topics
	result = bltd.get_word_frequency(analyze, True)
	print(result)  # accumulate and write as a block to DB
	for lemma, count in result.items():
		result_list += [{'lemma': lemma, 'article_body_id': article_body_id, 'lemma_count': count}]
	# write type: dict(lemma, article_body_id, lemma_count)
if db.write_lemmas(result_list, 1):
	print("successfully written to db)")
else:
	print("some error writing")
db.close()

