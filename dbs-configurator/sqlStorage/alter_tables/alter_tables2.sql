BEGIN;

ALTER TABLE news_meta_data.analyzer1_result ADD COLUMN sub_id integer NOT NULL DEFAULT 0;

COMMIT;
