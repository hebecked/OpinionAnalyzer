SELECT 
	CASE
		WHEN (udfs.udf_value IS NULL) THEN hdr.source_date
		ELSE to_date("substring"((udfs.udf_value)::text, 1, 10), 'YYYY-MM-DD'::text)
	END AS date,
	SUM(sentiment_value/ (error_value * error_value )) / SUM(1 / (error_value * error_value)) AS Sentiment1_error_weighted,
	AVG(sentiment_value) AS Sentiment2_simple_average,
	count(cmt.id) as Count_Comments
FROM news_meta_data.analyzer1_result AS rslt, 
		news_meta_data.article_body AS bdy,
		news_meta_data.article_header AS hdr,
		news_meta_data.comment AS cmt
	LEFT JOIN
		news_meta_data.udf_values as udfs
		ON udfs.object_id = cmt.id
WHERE 
		rslt.sub_id = 1 AND
		rslt.comment_id = cmt.id AND
		cmt.article_body_id = bdy.id AND
		hdr.id = bdy.article_id AND
		udfs.object_type = 2 AND
		udfs.udf_id = 4 AND
		cmt.body ilike '% merz%'

GROUP BY date
ORDER BY date DESC
