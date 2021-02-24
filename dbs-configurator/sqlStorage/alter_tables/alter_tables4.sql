BEGIN;

ALTER TABLE news_meta_data.crawl_dates_proc ADD CONSTRAINT crawl_dates_proc_srcid_dtproc_unique UNIQUE (source_id, date_processed);

COMMIT;