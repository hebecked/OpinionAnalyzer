BEGIN;

ALTER TABLE news_meta_data.comment ADD COLUMN IF NOT EXISTS date_created date NULL;

COMMIT;