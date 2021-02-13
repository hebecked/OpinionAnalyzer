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
bltd = BaselineTopicDetection()

#add a loop here
articles = db.fetch_topicizer_data()  # list of {article_body_id : dict {body: , headline: ,topics: } }
for article_id, article in articles.items():
	analyze = article["headline"] + " " + article["body"]
	
	#determine topics
	result = bltd.get_word_frequency(analyze, True)
	print(result)  # accumulate and write as a block to DB

db.close()

