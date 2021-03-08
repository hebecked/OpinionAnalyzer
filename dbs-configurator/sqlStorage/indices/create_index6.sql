BEGIN;

CREATE INDEX IF NOT EXISTS al_endtmstmp ON news_meta_data.analyzer_log(end_timestamp);

COMMIT;
