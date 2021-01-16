from utils.connectDb import Database
from utils.databaseExchange import DatabaseExchange
from TopicDetection import baseline_topic_detection
import json
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()


def test_db_connection():
    db = Database()
    db.connect()
    print("I am just here to say casually Hi....So, Hi! Oh and This: \n")
    db.getVersion()
    db.getTestTableMeta()

#init DB exchange module
db=DatabaseExchange()

#init baseline topic detection for analysis
bltd = baseline_topic_detection()

#add a loop here
articles = db.fetch_topicizer_data() # list of {article_body_id : dict {body: , headline: ,topics: } }
for article_id, article in articles.items():
	analyze = article["headline"] + " " + article["body"]
	
	#determine topics
	result = bltd.get_topics( analyze )
	print(result) # accumulate and write as a block to DB



