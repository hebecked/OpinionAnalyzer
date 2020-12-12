BEGIN;
--subquery for article_body_last
create or replace view news_meta_data.v_article_body_last_id as (select max(id) as last_article_body_id, article_id 
from news_meta_data.article_body
group by article_id);

--valid article headers with source information 
CREATE OR REPLACE VIEW news_meta_data.v_article_header_current AS (SELECT 
sth.type AS src_type,
sh.source AS src_name,
sh.id as src_id,
ah.id AS article_id,
ah.url,
ah.source_date,
ah.obsolete
FROM news_meta_data.source_header sh,
news_meta_data.source_type_header sth,
news_meta_data.article_header ah
WHERE sth.id = sh.type 
AND sh.id = ah.source_id 
AND ah.obsolete = false);

--last article_body record per article_id
create or replace view news_meta_data.v_article_body_last as (
select ab.*
from news_meta_data.v_article_body_last_id vabli,
news_meta_data.article_body ab
where ab.id = vabli.last_article_body_id);

--crawl_log todo list
create or replace view news_meta_data.v_todo_crawl as (
---missing body
select 
vahc.*,
vabl.id as article_body_id,
vabl.headline,
vabl.body,
vabl.proc_timestamp,
vabl.proc_counter,
0 as review_hours,
current_timestamp - interval '1 hour' as next_review,
'missing_body' as status
from news_meta_data.v_article_header_current vahc
left outer join news_meta_data.v_article_body_last vabl
on vahc.article_id = vabl.article_id
where vabl.article_id is null

union
--next review is now
select 
vahc.*,
vabl.id as article_body_id,
vabl.headline,
vabl.body,
vabl.proc_timestamp,
vabl.proc_counter,
(2^vabl.proc_counter) as review_hrs,
vabl.proc_timestamp + (interval '1 hour' * (2^vabl.proc_counter)) as next_review,
'review_now' as status
from news_meta_data.v_article_header_current vahc,
news_meta_data.v_article_body_last vabl
where vahc.article_id=vabl.article_id
and vabl.proc_counter < 14
and current_timestamp > vabl.proc_timestamp + (interval '1 hour' * ((2^vabl.proc_counter)-1)));

--analyzer_log todo list analyzer1
create or replace view news_meta_data.v_todo_analyzer1 as (
select 
c.id as comment_id,
al.analyzer_id,
al.start_timestamp,
al.end_timestamp,
al.success,
case
	when al.id is null
	then 'new'
	else 're-run'
end as status
from news_meta_data.comment c
left outer join news_meta_data.analyzer_log al 
on c.id = al.comment_id
where al.end_timestamp is null
and al.analyzer_id=1
);

COMMIT;