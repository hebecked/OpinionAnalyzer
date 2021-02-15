SELECT 
SUM(
	CASE WHEN obsolete THEN 1 ELSE 0 END
) 
/ COUNT(obsolete)::NUMERIC AS "% obsolete"

FROM news_meta_data.article_header WHERE source_id =3