from utils.connectDb import database
from Sentiment import EnsembleSentiment
from utils.databaseExchange import databaseExchange
import json

#init DB exchange module
db=databaseExchange()

#init the sentiment analyzer module
sentiment_analyzer=EnsembleSentiment()

#Fetch 1000 comments from the DB and anayze until all comments are analysed
while(comments := db.fetchTodoListAnalyzer(1)):
	sentiments=[]
	for comment in comments:
		sentiment=sentiment_analyzer.analyze(comment[1])
		db_entry={"ID": comment[0], "result": sentiment[0], "error": sentiment[1]}
		sentiments.append(db_entry)
		print( sentiment, comment)

 