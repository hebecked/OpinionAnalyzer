import logging

from Sentiment import EnsembleSentiment
from utils.databaseExchange import DatabaseExchange

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()

# init DB exchange module
db = DatabaseExchange()

# init the sentiment analyzer module
sentiment_analyzer = EnsembleSentiment()

# Fetch 1000 comments from the DB and anayze until all comments are analysed
while comments := db.fetch_analyzer_todo_list(1):
    logger.info("Starting analysis of " + str(len(comments)) + " (" + str(comments[0][0]) + "-" + str(
        comments[-1][0]) + ") comments and writing them to the database. This may take a while.")
    sentiments = []
    for comment in comments:
        sentiment = sentiment_analyzer.analyze(comment[1])
        db_entry1 = {"comment_id": comment[0], "sentiment_value": sentiment[0][0], "error_value": sentiment[0][1],
                     "sub_id": 1}
        db_entry2 = {"comment_id": comment[0], "sentiment_value": sentiment[1][0], "error_value": sentiment[1][1],
                     "sub_id": 2}
        db_entry3 = {"comment_id": comment[0], "sentiment_value": sentiment[2][0], "error_value": sentiment[2][1],
                     "sub_id": 3}
        sentiments.append(db_entry1)
        sentiments.append(db_entry2)
        sentiments.append(db_entry3)
    db.write_analyzer_results(1, sentiments)
    logger.info('Analyzed comment ' + str(sentiments[1]["comment_id"]) + ' to ' + str(
        sentiments[-1]["comment_id"]) + " and wrote to DB.")
