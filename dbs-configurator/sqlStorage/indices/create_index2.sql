BEGIN;

CREATE INDEX ah_src_id ON news_meta_data.article_header(source_id);

COMMIT;
