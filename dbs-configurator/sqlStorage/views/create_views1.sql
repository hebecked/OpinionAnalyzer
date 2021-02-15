BEGIN;

--topic detection with sources 
CREATE OR REPLACE VIEW news_meta_data.v_topics_detected_src AS ( 
select distinct
ah.source_id as article_source_id,
sh.source as article_source,
tdr.topic_detector_id,
tdh.topic_detector,
tdr.lemma_id,
lh.lemma
from news_meta_data.source_header sh, 
news_meta_data.article_header ah, 
news_meta_data.topic_detector_result tdr, 
news_meta_data.topic_detector_header tdh,
news_meta_data.lemma_header lh
where ah.id =  tdr.article_header_id
and tdr.lemma_id = lh.id
and sh.id = ah.source_id
and tdh.id = tdr.topic_detector_id
);

--drop v_todo_analyzer1_next
drop view news_meta_data.v_todo_analyzer1_next;

--drop v_todo_analyzer1
drop view news_meta_data.v_todo_analyzer1;

--analyzer_log todo list analyzer1
create or replace view news_meta_data.v_todo_analyzer1 as (
 SELECT c.id AS comment_id,
    c.level AS comment_level,
    c.body AS comment_body,
    ah.source_date,
    al.analyzer_id,
    al.start_timestamp,
    al.end_timestamp,
    al.success,
        CASE
            WHEN al.id IS NULL THEN 'new'::text
            ELSE 're-run'::text
        END AS status
   FROM news_meta_data.article_body ab, news_meta_data.article_header ah, news_meta_data.comment c
     LEFT JOIN news_meta_data.analyzer_log al ON c.id = al.comment_id
  WHERE ah.id=ab.article_id
  and ab.id=c.article_body_id
  and (al.id IS NULL OR (al.id IS NOT NULL AND al.analyzer_id = 1 AND al.end_timestamp is NULL))
);

--top 1000 of todo_analyzer1
create or replace view news_meta_data.v_todo_analyzer1_next as (
select 
comment_id,
comment_level,
comment_body,
source_date,
analyzer_id,
start_timestamp,
end_timestamp,
success,
status
from news_meta_data.v_todo_analyzer1
where comment_level = 0
and start_timestamp is null
order by source_date desc
limit 1000
);

COMMIT;