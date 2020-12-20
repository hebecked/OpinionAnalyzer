from utils.connectDb import database
from Sentiment import EnsembleSentiment
from utils.databaseExchange import databaseExchange
import json


db=databaseExchange()

sentiment_analyzer=EnsembleSentiment()
while(comments := db.fetchTodoListAnalyzer(1)):
	sentiments=[]
	for comment in comments:
		sentiment=sentiment_analyzer.analyze(comment[1])
		db_entry={"ID": comment[0], "result": sentiment[0], "error": sentiment[1]}
		sentiments.append(db_entry)
		print( sentiment, comment)

 