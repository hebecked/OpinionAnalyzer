BEGIN;

CREATE INDEX IF NOT EXISTS uv_udf_id ON news_meta_data.udf_values(udf_id);

COMMIT;
