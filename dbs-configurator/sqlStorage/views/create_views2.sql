BEGIN;

--topic detection with sources 
create or replace view news_meta_data.v_comment_date_created_empty as (
select
ah.id as ah_id,
ab.id as ab_id,
co.id as co_id
from news_meta_data.comment co, news_meta_data.article_body ab, news_meta_data.article_header ah
where ah.id=ab.article_id
and ab.id=co.article_body_id
and co.date_created is null);

COMMIT;