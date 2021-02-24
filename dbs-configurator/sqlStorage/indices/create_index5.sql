BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS co_body_trgm ON news_meta_data.comment USING gin (body gin_trgm_ops);
CREATE INDEX IF NOT EXISTS ab_body_trgm ON news_meta_data.article_body USING gin (body gin_trgm_ops);
CREATE INDEX IF NOT EXISTS co_dt_crtd ON news_meta_data.comment(date_created);
CREATE INDEX IF NOT EXISTS co_proc_tmstmp ON news_meta_data.comment(proc_timestamp);

COMMIT;
