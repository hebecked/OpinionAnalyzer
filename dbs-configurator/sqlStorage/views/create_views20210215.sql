BEGIN;

create or replace view news_meta_data.v_todo_lemmatizer as (select
	ah.source_date,
	ab.id as ab_id,
	ab.headline,
	ab.body
from news_meta_data.article_header ah,
	news_meta_data.article_body ab
left join news_meta_data.lemma_count lc on ab.id = lc.article_body_id
where ah.id=ab.article_id
and lc.lemma_id is null
and ab.body != ''
order by ah.source_date desc
limit 1000);

COMMIT;