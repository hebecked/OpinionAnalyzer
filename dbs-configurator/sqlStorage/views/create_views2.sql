BEGIN;

--show all comment records without date_created that are older than 3 hrs processing time
CREATE OR REPLACE VIEW news_meta_data.v_comment_date_created_empty as (
SELECT ah.id AS ah_id,
    ab.id AS ab_id,
    co.id AS co_id
   FROM news_meta_data.comment co,
    news_meta_data.article_body ab,
    news_meta_data.article_header ah
  WHERE ah.id = ab.article_id 
  AND ab.id = co.article_body_id 
  AND co.date_created IS NULL
  AND co.proc_timestamp < (NOW() - INTERVAL '3 hours')
);

COMMIT;