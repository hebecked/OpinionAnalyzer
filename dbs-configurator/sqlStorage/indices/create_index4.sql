BEGIN;

CREATE INDEX IF NOT EXISTS uv_udf_id ON news_meta_data.udf_values(udf_id);
CREATE INDEX IF NOT EXISTS co_body ON news_meta_data.comment USING GIN (to_tsvector('german',body));
CREATE INDEX IF NOT EXISTS ab_body ON news_meta_data.article_body USING GIN (to_tsvector('german',body));


COMMIT;
