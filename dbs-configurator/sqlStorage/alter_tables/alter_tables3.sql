BEGIN;

ALTER TABLE news_meta_data.crawl_dates_proc ADD FOREIGN KEY (source_id) REFERENCES news_meta_data.source_header (id) ON DELETE CASCADE;

COMMIT;
