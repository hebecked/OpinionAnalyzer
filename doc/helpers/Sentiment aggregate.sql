SELECT 
	cmt.date_created AS date,
	SUM(sentiment_value/ (error_value * error_value )) / SUM(1 / (error_value * error_value)) AS Sentiment1_error_weighted,
	AVG(sentiment_value) AS Sentiment2_simple_average,
	count(cmt.id) as Count_Comments
FROM news_meta_data.analyzer1_result AS rslt, 
	news_meta_data.comment AS cmt
WHERE 
	rslt.comment_id = cmt.id AND
	cmt.body ilike '% merz%'

GROUP BY date
ORDER BY date DESC
