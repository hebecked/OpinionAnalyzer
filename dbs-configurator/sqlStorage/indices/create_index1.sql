BEGIN;

CREATE INDEX ah_src_dt ON news_meta_data.article_header(source_date);

COMMIT;
