from utils.connectDb import database
from Sentiment import EnsembleSentiment
from utils.databaseExchange import databaseExchange
import json
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()

#init DB exchange module
db=databaseExchange()

#init the sentiment analyzer module
sentiment_analyzer=EnsembleSentiment()

#Fetch 1000 comments from the DB and anayze until all comments are analysed
while(comments := db.fetchTodoListAnalyzer(1)):
	sentiments=[]
	for comment in comments:
		print("Test2")
		sentiment=sentiment_analyzer.analyze(comment[1])
		db_entry={"comment_id": comment[0], "sentiment_value": sentiment[0], "error_value": sentiment[1]}
		sentiments.append(db_entry)
	print("Test3")
	db.writeAnalyzerResults(1, sentiments)
	logger.info('Analyzed comment ' + str(sentiments[1]["comment_id"]) + ' to ' + str(sentiments[-1]["comment_id"]) + " and wrote to DB.")


 