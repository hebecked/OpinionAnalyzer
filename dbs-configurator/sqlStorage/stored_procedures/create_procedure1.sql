CREATE OR REPLACE PROCEDURE news_meta_data.update_comment_date_created()
LANGUAGE SQL
AS $$
---update from udf
update news_meta_data.comment co
	set date_created = TO_DATE(substring(ud.udf_value,1,10),'YYYY-MM-DD')
	from news_meta_data.udf_values ud
	where co.date_created is null
	and co.id=ud.object_id
	and ud.object_type=2
	and ud.udf_id=4;
---update from article_header
update news_meta_data.comment co
	set date_created = ah.source_date
	from news_meta_data.v_comment_date_created_empty v,
	news_meta_data.article_header ah 
	where v.ah_id=ah.id
	and v.co_id=co.id;
$$;
