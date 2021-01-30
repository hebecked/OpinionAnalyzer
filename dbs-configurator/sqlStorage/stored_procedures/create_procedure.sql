CREATE OR REPLACE PROCEDURE news_meta_data.update_topic_lemma()
LANGUAGE SQL
AS $$
insert into news_meta_data.lemma_header (lemma) select distinct substr(lower(udf_value), 1, 30)
from news_meta_data.udf_values
where object_type=1
and udf_id=2
and substr(lower(udf_value), 1, 30) not in (select lemma from news_meta_data.lemma_header)
and object_id > (select case when max(article_header_id) is null then 0 else max(article_header_id) end
from news_meta_data.topic_detector_result);
insert into news_meta_data.topic_detector_result (article_header_id, topic_detector_id, lemma_id, run_date)
select distinct vabli.article_id, 1, lh.id, NOW()
from news_meta_data.v_article_body_last_id vabli, news_meta_data.lemma_header lh, news_meta_data.udf_values uv
where 
--article_body
uv.object_type=1
--label
and uv.udf_id=2
and vabli.last_article_body_id = uv.object_id
and lh.lemma=substr(lower(uv.udf_value), 1, 30)
and vabli.article_id > (select case when max(article_header_id) is null then 0 else max(article_header_id) end
from news_meta_data.topic_detector_result);
$$;
